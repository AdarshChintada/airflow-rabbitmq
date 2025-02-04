db = db.getSiblingDB('schedule_db');

db.createCollection('client_schedule');

db.my_collection.insertMany([{
    "_id": {
      "$oid": "67889059d8dc5fb4860ddb98"
    },
    "client_id": 1,
    "email": "adarshchintada2@gmail.com",
    "schedule_ist": "30 10 * * *",
    "services": [
      "email"
    ]
  },
  {
    "_id": {
      "$oid": "67889059d8dc5fb4860ddb99"
    },
    "client_id": 2,
    "email": "adarsh.chintada@nimbleaccounting.com",
    "schedule_ist": "45 10 * * *",
    "services": [
      "email"
    ]
  },
  {
    "_id": {
      "$oid": "678890bed8dc5fb4860ddb9b"
    },
    "client_id": 3,
    "email": "n180479@rguktn.ac.in",
    "schedule_ist": "30 10 * * *",
    "services": [
      "email",
      "sms"
    ]
  }]);
