from flask import Flask, request, jsonify,render_template
import math

app = Flask(__name__)

# Blood compatibility: recipient -> possible donor groups
COMPATIBILITY = {
    "O+": ["O+", "O-"],
    "O-": ["O-"],
    "A+": ["A+", "A-", "O+", "O-"],
    "A-": ["A-", "O-"],
    "B+": ["B+", "B-", "O+", "O-"],
    "B-": ["B-", "O-"],
    "AB+": ["AB+", "AB-", "A+", "A-", "B+", "B-", "O+", "O-"],
    "AB-": ["AB-", "A-", "B-", "O-"]
}

# Sample donor database
donors = [
    {
        "id": 1,
        "name": "Ravi",
        "blood_group": "O+",
        "available": True,
        "lat": 14.6819,
        "lon": 78.9888
    },
    {
        "id": 2,
        "name": "Priya",
        "blood_group": "A+",
        "available": True,
        "lat": 14.6750,
        "lon": 78.9900
    },
    {
        "id": 3,
        "name": "Arjun",
        "blood_group": "B+",
        "available": False,
        "lat": 14.6900,
        "lon": 78.9800
    },
    {
        "id": 4,
        "name": "Sneha",
        "blood_group": "O-",
        "available": True,
        "lat": 14.6800,
        "lon": 78.9850
    }
]


def distance(lat1, lon1, lat2, lon2):
    """Calculate distance between two locations in km."""
    R = 6371

    lat1 = math.radians(lat1)
    lat2 = math.radians(lat2)

    dlat = lat2 - lat1
    dlon = math.radians(lon2 - lon1)

    a = (math.sin(dlat / 2) ** 2 +
         math.cos(lat1) * math.cos(lat2) *
         math.sin(dlon / 2) ** 2)

    return R * 2 * math.atan2(math.sqrt(a), math.sqrt(1 - a))


def match_score(donor, required_group, hospital_lat, hospital_lon):
    score = 0

    # Blood group compatibility
    if donor["blood_group"] in COMPATIBILITY[required_group]:
        score += 50

    # Availability
    if donor["available"]:
        score += 30

    # Distance
    dist = distance(
        donor["lat"],
        donor["lon"],
        hospital_lat,
        hospital_lon
    )

    if dist <= 5:
        score += 20
    elif dist <= 10:
        score += 15
    elif dist <= 20:
        score += 10
    else:
        score += 5

    return score, round(dist, 2)
@app.route("/")
def home():
    return 
render_template("test.html")
@app.route("/test")
def test_page():
    return send_from_directory(".", "test.html")
@app.route("/match-donors", methods=["POST"])
def match_donors():

    data = request.json

    required_group = data["blood_group"]
    hospital_lat = float(data["latitude"])
    hospital_lon = float(data["longitude"])

    matches = []

    for donor in donors:

        if not donor["available"]:
            continue

        if donor["blood_group"] not in COMPATIBILITY[required_group]:
            continue

        score, dist = match_score(
            donor,
            required_group,
            hospital_lat,
            hospital_lon
        )

        matches.append({
            "donor_id": donor["id"],
            "name": donor["name"],
            "blood_group": donor["blood_group"],
            "distance_km": dist,
            "match_score": score,
            "status": "Suitable Donor"
        })

    # Highest score first
    matches.sort(
        key=lambda x: x["match_score"],
        reverse=True
    )

    return jsonify({
        "required_blood_group": required_group,
        "total_matches": len(matches),
        "recommended_donors": matches
    })


if __name__ == "__main__":
    app.run(debug=True)