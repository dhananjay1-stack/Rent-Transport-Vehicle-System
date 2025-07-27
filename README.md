Goods Transportation System
📌 Project Overview
The Goods Transportation System is a web-based platform that connects customers needing transportation services with hosts who own goods carriers. It provides real-time carrier tracking, booking management, and feedback systems to ensure transparency, efficiency, and convenience.

💡 Main Users:

Customers – Individuals or businesses who book goods carriers.

Hosts – Owners who manage carriers and respond to bookings.

📖 Table of Contents
Features

System Architecture

Database Models

Location Tracking

Technologies Used

Getting Started

Contributing

License

✅ Features
👤 Customer Features
Login/Signup and personalized dashboard

View and filter available goods carriers

Book a carrier by location, price, or availability

Access booking history and booking confirmation

Real-time tracking of booked carriers

Provide feedback for completed services

🧑‍🔧 Host Features
Host dashboard with full carrier management

Add/update/delete goods carriers

Track carrier locations in real-time

View and manage active bookings

Respond to customer feedback

🏗️ System Architecture
The platform supports two major user roles:

1. Customers
View profile and booking history

Filter and select from available carriers

Book carriers with real-time confirmation

Track carrier location after booking

Submit feedback

2. Hosts
Manage carrier details (add, edit, delete)

Monitor carrier location using latitude/longitude

View current/active bookings

Respond to customer feedback

🗃️ Database Models
📦 Host Model
Stores information about the host and links to their user profile.

Fields:

user: One-to-One relationship with the user model

name, address, city, state, country, pin_code, phone_number

🚛 GoodsCarrier Model
Represents vehicles owned by hosts.

Fields:

host: Foreign key linking to Host

name, carrier_number (unique), owner_name, phone_number

rate_per_hour, photo, availability_status

latitude, longitude, location, available (boolean)

📍 Location Tracking
🔄 Real-Time Carrier Tracking
For Hosts: Monitor live location of all listed carriers

For Customers: View real-time updates once a carrier is booked

Benefits:

Enhanced delivery/pick-up time accuracy

Transparency in movement and status

Improved fleet management and response time

🧰 Technologies Used
Frontend: HTML, CSS, JavaScript (or React.js)

Backend: Python (Django or Flask), Node.js (Express)

Database: PostgreSQL, MongoDB (optional hybrid)

Authentication: Firebase Auth / JWT-based Auth

APIs: Google Maps API (for real-time tracking)

