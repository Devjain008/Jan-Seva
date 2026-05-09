# backend/predictive.py
"""
Predictive Governance Module
Analyzes complaint patterns to predict future issues
"""

from sqlalchemy.orm import Session
from backend import models
from datetime import datetime, timedelta
from collections import defaultdict, Counter
from typing import List, Dict, Any
import math

class PredictiveAnalytics:
    """Predictive analytics engine for complaint patterns"""
    
    def __init__(self, db: Session):
        self.db = db
    
    def get_complaint_trends(self, days_back: int = 30) -> Dict[str, Any]:
        """Analyze complaint trends over time period"""
        cutoff = datetime.utcnow() - timedelta(days=days_back)
        
        complaints = self.db.query(models.Complaint).filter(
            models.Complaint.created_at >= cutoff
        ).all()
        
        # Category trends
        category_trend = defaultdict(int)
        department_trend = defaultdict(int)
        location_trend = defaultdict(lambda: {"count": 0, "complaints": [], "categories": Counter()})
        
        for c in complaints:
            category_trend[c.category] += 1
            if c.department_id:
                department_trend[c.department_id] += 1
            
            # Location-based tracking
            loc_key = self._normalize_location(c.location or "")
            if loc_key:
                location_trend[loc_key]["count"] += 1
                location_trend[loc_key]["complaints"].append({
                    "id": c.complaint_id,
                    "category": c.category,
                    "priority": c.priority,
                    "created_at": c.created_at.isoformat()
                })
                location_trend[loc_key]["categories"][c.category] += 1
        
        return {
            "total_complaints": len(complaints),
            "period_days": days_back,
            "category_trend": dict(category_trend),
            "department_trend": dict(department_trend),
            "locations": dict(location_trend)
        }
    
    def detect_risk_zones(self, threshold: int = 3, days_back: int = 30) -> List[Dict[str, Any]]:
        """
        Detect areas at risk of future complaints
        
        Risk factors:
        1. High frequency of complaints in same area
        2. Recurring complaints of same category
        3. Escalating priority patterns
        4. Seasonal/Time-based patterns
        """
        cutoff = datetime.utcnow() - timedelta(days=days_back)
        
        complaints = self.db.query(models.Complaint).filter(
            models.Complaint.created_at >= cutoff
        ).all()
        
        # Group by location
        location_data = defaultdict(lambda: {
            "count": 0,
            "categories": Counter(),
            "priorities": Counter(),
            "recent_count": 0,
            "complaint_ids": [],
            "first_seen": None,
            "last_seen": None,
            "recurrence_rate": 0,
            "trend": "stable"
        })
        
        for c in complaints:
            loc = self._normalize_location(c.location or "Unknown Area")
            data = location_data[loc]
            data["count"] += 1
            data["categories"][c.category] += 1
            data["priorities"][c.priority] += 1
            data["complaint_ids"].append(c.complaint_id)
            
            if data["first_seen"] is None or c.created_at < data["first_seen"]:
                data["first_seen"] = c.created_at
            if data["last_seen"] is None or c.created_at > data["last_seen"]:
                data["last_seen"] = c.created_at
            
            # Count recent complaints (last 7 days)
            if c.created_at >= datetime.utcnow() - timedelta(days=7):
                data["recent_count"] += 1
        
        # Calculate risk scores
        risk_zones = []
        for location, data in location_data.items():
            if data["count"] < threshold:
                continue
            
            # Risk scoring factors
            frequency_score = min(data["count"] / threshold, 3)  # 0-3
            
            # Recurrence: same category repeated
            top_category, top_count = data["categories"].most_common(1)[0]
            recurrence_score = min(top_count / data["count"] * 2, 2)  # 0-2
            
            # Escalation: high priority complaints
            high_priority_ratio = data["priorities"].get("high", 0) / data["count"]
            escalation_score = high_priority_ratio * 2  # 0-2
            
            # Recent activity surge
            recent_ratio = data["recent_count"] / max(data["count"] / 4, 1)
            surge_score = min(recent_ratio, 1.5)  # 0-1.5
            
            # Calculate total risk score (max 10)
            total_risk = frequency_score + recurrence_score + escalation_score + surge_score
            
            # Determine risk level
            if total_risk >= 7:
                risk_level = "critical"
                risk_color = "#dc2626"
                action_text = "Immediate action required"
            elif total_risk >= 4.5:
                risk_level = "high"
                risk_color = "#d97706"
                action_text = "Intervention needed soon"
            elif total_risk >= 2.5:
                risk_level = "medium"
                risk_color = "#eab308"
                action_text = "Monitor closely"
            else:
                risk_level = "low"
                risk_color = "#10b981"
                action_text = "Routine monitoring"
            
            # Calculate predicted time to next complaint
            days_between = self._calculate_predicted_interval(data)
            
            # Determine trend direction
            trend = self._calculate_trend(location_data[location], complaints)
            
            risk_zones.append({
                "location": location,
                "risk_level": risk_level,
                "risk_color": risk_color,
                "risk_score": round(total_risk, 1),
                "complaint_count": data["count"],
                "recent_count": data["recent_count"],
                "top_category": top_category,
                "top_category_count": top_count,
                "category_distribution": dict(data["categories"]),
                "priority_distribution": dict(data["priorities"]),
                "predicted_next_complaint_days": days_between,
                "trend": trend,
                "action_required": action_text,
                "first_seen": data["first_seen"].isoformat() if data["first_seen"] else None,
                "last_seen": data["last_seen"].isoformat() if data["last_seen"] else None,
            })
        
        # Sort by risk score (highest first)
        risk_zones.sort(key=lambda x: x["risk_score"], reverse=True)
        return risk_zones
    
    def predict_department_workload(self, days_ahead: int = 7) -> List[Dict[str, Any]]:
        """Predict workload for each department"""
        cutoff = datetime.utcnow() - timedelta(days=30)
        
        complaints = self.db.query(models.Complaint).filter(
            models.Complaint.created_at >= cutoff
        ).all()
        
        dept_workload = defaultdict(lambda: {
            "daily_avg": 0,
            "trend": "stable",
            "predicted_complaints": 0,
            "current_backlog": 0,
            "resolution_rate": 0
        })
        
        for c in complaints:
            if c.department_id:
                dept_workload[c.department_id]["current_backlog"] += 1 if c.status in ["pending", "in_progress"] else 0
        
        # Calculate daily averages and predictions
        for dept_id in dept_workload:
            dept_complaints = [c for c in complaints if c.department_id == dept_id]
            if dept_complaints:
                days_span = (datetime.utcnow() - cutoff).days or 1
                daily_avg = len(dept_complaints) / days_span
                dept_workload[dept_id]["daily_avg"] = round(daily_avg, 1)
                dept_workload[dept_id]["predicted_complaints"] = round(daily_avg * days_ahead)
                
                # Calculate resolution rate
                resolved = len([c for c in dept_complaints if c.status in ["resolved", "closed"]])
                dept_workload[dept_id]["resolution_rate"] = round(resolved / len(dept_complaints) * 100, 1)
        
        # Get department names
        result = []
        for dept_id, workload in dept_workload.items():
            dept = self.db.query(models.Department).filter(models.Department.id == dept_id).first()
            result.append({
                "department_id": dept_id,
                "department_name": dept.name if dept else "Unknown",
                "daily_avg_complaints": workload["daily_avg"],
                "predicted_complaints_7d": workload["predicted_complaints"],
                "current_backlog": workload["current_backlog"],
                "resolution_rate": workload["resolution_rate"],
            })
        
        return sorted(result, key=lambda x: x["predicted_complaints_7d"], reverse=True)
    
    def get_hotspots(self, top_n: int = 5) -> List[Dict[str, Any]]:
        """Identify geographic hotspots from geotagged complaints"""
        cutoff = datetime.utcnow() - timedelta(days=30)
        
        complaints = self.db.query(models.Complaint).filter(
            models.Complaint.created_at >= cutoff,
            models.Complaint.latitude.isnot(None),
            models.Complaint.longitude.isnot(None)
        ).all()
        
        # Cluster nearby complaints (simplified grid-based clustering)
        grid_size = 0.01  # ~1km grid
        clusters = defaultdict(lambda: {
            "count": 0,
            "lat_sum": 0,
            "lon_sum": 0,
            "categories": Counter(),
            "complaints": []
        })
        
        for c in complaints:
            if c.latitude and c.longitude:
                grid_key = (round(c.latitude / grid_size), round(c.longitude / grid_size))
                cluster = clusters[grid_key]
                cluster["count"] += 1
                cluster["lat_sum"] += c.latitude
                cluster["lon_sum"] += c.longitude
                cluster["categories"][c.category] += 1
                cluster["complaints"].append({
                    "id": c.complaint_id,
                    "priority": c.priority
                })
        
        # Convert to hotspots
        hotspots = []
        for grid_key, cluster in clusters.items():
            if cluster["count"] >= 3:  # Minimum complaints for hotspot
                hotspots.append({
                    "latitude": cluster["lat_sum"] / cluster["count"],
                    "longitude": cluster["lon_sum"] / cluster["count"],
                    "complaint_count": cluster["count"],
                    "top_category": cluster["categories"].most_common(1)[0][0] if cluster["categories"] else "unknown",
                    "risk_score": min(cluster["count"] * 1.5, 10),
                })
        
        hotspots.sort(key=lambda x: x["complaint_count"], reverse=True)
        return hotspots[:top_n]
    
    def generate_alert_summary(self) -> Dict[str, Any]:
        """Generate summary alerts for admin dashboard"""
        risk_zones = self.detect_risk_zones()
        workload = self.predict_department_workload()
        hotspots = self.get_hotspots()
        
        # Count risk levels
        risk_counts = {"critical": 0, "high": 0, "medium": 0, "low": 0}
        for zone in risk_zones:
            risk_counts[zone["risk_level"]] += 1
        
        # Generate alert messages
        alerts = []
        
        if risk_counts["critical"] > 0:
            alerts.append({
                "type": "critical",
                "message": f"⚠️ {risk_counts['critical']} critical risk zone(s) detected requiring immediate attention",
                "action_required": True
            })
        
        if risk_counts["high"] > 0:
            alerts.append({
                "type": "warning",
                "message": f"📊 {risk_counts['high']} high-risk area(s) showing concerning complaint patterns",
                "action_required": True
            })
        
        # Check for departments with high predicted workload
        for dept in workload[:3]:
            if dept["predicted_complaints_7d"] > 20:
                alerts.append({
                    "type": "info",
                    "message": f"🏢 {dept['department_name']} predicted to receive {dept['predicted_complaints_7d']} complaints in next 7 days",
                    "action_required": False
                })
        
        return {
            "total_risk_zones": len(risk_zones),
            "risk_breakdown": risk_counts,
            "active_alerts": alerts,
            "top_risk_zones": risk_zones[:5],
            "predicted_hotspots": hotspots,
            "department_workload_forecast": workload[:5],
            "generated_at": datetime.utcnow().isoformat()
        }
    
    def _normalize_location(self, location: str) -> str:
        """Normalize location string for consistent grouping"""
        if not location:
            return "Unknown Area"
        # Remove common prefixes and normalize
        loc = location.lower().strip()
        # Remove area, ward, sector prefixes
        replacements = [
            ("ward", ""), ("sector", ""), ("block", ""), 
            ("area", ""), ("zone", ""), ("colony", ""),
            ("nagar", ""), ("basti", ""),
        ]
        for old, new in replacements:
            loc = loc.replace(old, new)
        # Take first 30 chars as key
        return loc[:30].strip().title()
    
    def _calculate_predicted_interval(self, data: Dict) -> int:
        """Calculate predicted days until next complaint"""
        if data["count"] < 2:
            return 14  # Default 2 weeks
        
        # Calculate average days between complaints
        dates = []
        # Simplified: use first and last
        if data["first_seen"] and data["last_seen"]:
            days_span = (data["last_seen"] - data["first_seen"]).days or 1
            avg_interval = days_span / (data["count"] - 1)
            return max(1, min(int(avg_interval), 30))  # Clamp between 1-30 days
        
        return 7  # Default 1 week
    
    def _calculate_trend(self, data: Dict, all_complaints: List) -> str:
        """Calculate trend direction"""
        if data["recent_count"] > (data["count"] * 0.4):
            return "increasing"
        elif data["recent_count"] < (data["count"] * 0.1):
            return "decreasing"
        return "stable"