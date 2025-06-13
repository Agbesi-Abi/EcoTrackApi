"""
Activity utilities for EcoTrack Ghana
"""

import aiofiles
import os
import uuid
from datetime import datetime
from pathlib import Path
from fastapi import UploadFile, HTTPException
from typing import Dict, Any

from database import User

def calculate_points(activity_type: str, activity_data: Dict[str, Any]) -> int:
    """Calculate points for an activity based on type and data"""
    
    base_points = {
        'trash': 25,
        'trees': 50,
        'mobility': 15,
        'water': 20,
        'energy': 30
    }
    
    points = base_points.get(activity_type, 10)
    
    # Bonus points for different factors
    if activity_data.get('photos'):
        points += 5  # Photo documentation bonus
    
    if activity_data.get('location'):
        points += 3  # Location sharing bonus
    
    # Type-specific bonuses
    if activity_type == 'trash':
        # Bonus for larger cleanup efforts
        if 'impact_data' in activity_data:
            bags = activity_data['impact_data'].get('bags_collected', 0)
            if bags > 0:
                points += min(bags * 5, 25)  # Max 25 bonus points
    
    elif activity_type == 'trees':
        # Bonus for multiple trees
        if 'impact_data' in activity_data:
            trees = activity_data['impact_data'].get('trees_planted', 1)
            if trees > 1:
                points += (trees - 1) * 20  # 20 points per additional tree
    
    elif activity_type == 'mobility':
        # Bonus for longer distances or duration
        if 'impact_data' in activity_data:
            distance = activity_data['impact_data'].get('distance_km', 0)
            if distance > 0:
                points += min(int(distance), 15)  # Max 15 bonus points
    
    return min(points, 200)  # Cap at 200 points per activity

def update_user_impact_stats(user: User, activity_type: str, activity_data: Dict[str, Any]):
    """Update user's environmental impact statistics"""
    
    if activity_type == 'trash':
        # Estimate trash collected (assume 1 bag = 2kg)
        bags = activity_data.get('impact_data', {}).get('bags_collected', 1)
        user.trash_collected += bags * 2.0
        user.co2_saved += bags * 0.5  # Estimated CO2 saved per bag
    
    elif activity_type == 'trees':
        # Trees planted
        trees = activity_data.get('impact_data', {}).get('trees_planted', 1)
        user.trees_planted += trees
        user.co2_saved += trees * 21.77  # Average CO2 absorbed per tree per year
    
    elif activity_type == 'mobility':
        # CO2 saved from sustainable transport
        distance = activity_data.get('impact_data', {}).get('distance_km', 5)
        transport_type = activity_data.get('impact_data', {}).get('transport_type', 'walking')
        
        # CO2 emission factors (kg CO2 per km)
        emission_factors = {
            'walking': 0,
            'cycling': 0,
            'public_transport': 0.05,
            'car_pooling': 0.1  # Reduced emissions due to sharing
        }
        
        # Assume saved vs. driving alone (0.2 kg CO2 per km)
        saved_emissions = distance * (0.2 - emission_factors.get(transport_type, 0.05))
        user.co2_saved += max(saved_emissions, 0)
    
    elif activity_type == 'water':
        # Water conservation
        liters_saved = activity_data.get('impact_data', {}).get('water_saved_liters', 50)
        # Indirect CO2 savings from water conservation
        user.co2_saved += liters_saved * 0.0003  # Estimated CO2 per liter of water treatment
    
    elif activity_type == 'energy':
        # Energy conservation
        kwh_saved = activity_data.get('impact_data', {}).get('energy_saved_kwh', 5)
        # CO2 savings from reduced energy consumption (Ghana grid factor)
        user.co2_saved += kwh_saved * 0.45  # kg CO2 per kWh in Ghana

async def save_uploaded_file(file: UploadFile, folder: str) -> str:
    """Save uploaded file and return URL"""
    
    # Create upload directory
    upload_dir = Path("uploads") / folder
    upload_dir.mkdir(parents=True, exist_ok=True)
    
    # Generate unique filename
    file_extension = file.filename.split(".")[-1] if "." in file.filename else "jpg"
    filename = f"{uuid.uuid4()}.{file_extension}"
    file_path = upload_dir / filename
    
    # Check file size (5MB limit)
    MAX_FILE_SIZE = 5 * 1024 * 1024
    content = await file.read()
    if len(content) > MAX_FILE_SIZE:
        raise HTTPException(status_code=413, detail="File too large")
    
    # Save file
    async with aiofiles.open(file_path, 'wb') as f:
        await f.write(content)
    
    # Return relative URL
    return f"/uploads/{folder}/{filename}"

def get_impact_summary(activities: list) -> Dict[str, Any]:
    """Calculate impact summary from activities"""
    
    total_points = sum(activity.points for activity in activities)
    activity_counts = {}
    
    for activity in activities:
        activity_type = activity.type
        activity_counts[activity_type] = activity_counts.get(activity_type, 0) + 1
    
    return {
        "total_activities": len(activities),
        "total_points": total_points,
        "activities_by_type": activity_counts,
        "recent_activity": activities[0].created_at if activities else None
    }
