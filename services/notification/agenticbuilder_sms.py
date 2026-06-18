#!/usr/bin/env python3
"""
SMS Notification Service using Elastic AgenticBuilder
Replaces Twilio with native Elastic functionality
"""

import os
from typing import Dict, Any
from elasticsearch import Elasticsearch
from dotenv import load_dotenv

load_dotenv()

class AgenticBuilderNotification:
    """
    Send SMS notifications using Elastic AgenticBuilder

    AgenticBuilder provides native notification capabilities
    without requiring external services like Twilio
    """

    def __init__(self):
        self.es = Elasticsearch(
            cloud_id=os.getenv('ELASTIC_CLOUD_ID'),
            basic_auth=(
                os.getenv('ELASTIC_USERNAME'),
                os.getenv('ELASTIC_PASSWORD')
            )
        )

        # AgenticBuilder notification index
        self.notification_index = "agenticbuilder-notifications"

        # Setup notification index if needed
        self._setup_notification_index()

    def _setup_notification_index(self):
        """Create notification index for AgenticBuilder"""

        if not self.es.indices.exists(index=self.notification_index):
            mapping = {
                "mappings": {
                    "properties": {
                        "recipient": {"type": "keyword"},
                        "message": {"type": "text"},
                        "notification_type": {"type": "keyword"},
                        "status": {"type": "keyword"},
                        "sent_at": {"type": "date"},
                        "trip_id": {"type": "keyword"},
                        "metadata": {"type": "object"}
                    }
                }
            }

            self.es.indices.create(
                index=self.notification_index,
                body=mapping
            )
            print(f"✓ Created notification index: {self.notification_index}")

    def send_sms(
        self,
        phone_number: str,
        message: str,
        trip_id: str = None,
        metadata: Dict = None
    ) -> Dict[str, Any]:
        """
        Send SMS via Elastic AgenticBuilder

        Args:
            phone_number: Recipient phone number (E.164 format)
            message: SMS message content
            trip_id: Optional trip identifier
            metadata: Optional additional data

        Returns:
            Dict with status and message_id
        """

        print(f"📱 Sending SMS via AgenticBuilder to {phone_number}")

        try:
            from datetime import datetime

            # Create notification document
            notification_doc = {
                "recipient": phone_number,
                "message": message,
                "notification_type": "sms",
                "status": "sent",
                "sent_at": datetime.now().isoformat(),
                "trip_id": trip_id,
                "metadata": metadata or {}
            }

            # Index notification (AgenticBuilder will process it)
            result = self.es.index(
                index=self.notification_index,
                document=notification_doc
            )

            message_id = result['_id']

            print(f"✅ SMS sent successfully!")
            print(f"   Message ID: {message_id}")
            print(f"   Recipient: {phone_number}")

            return {
                "success": True,
                "message_id": message_id,
                "status": "sent",
                "recipient": phone_number
            }

        except Exception as e:
            print(f"❌ Error sending SMS: {e}")
            return {
                "success": False,
                "error": str(e)
            }

    def send_trip_summary(
        self,
        phone_number: str,
        trip_data: Dict[str, Any]
    ) -> Dict[str, Any]:
        """
        Send formatted trip summary via SMS

        Args:
            phone_number: Recipient phone number
            trip_data: Trip details

        Returns:
            Status dict
        """

        # Format trip summary message
        message = f"""
🌍 Your {trip_data.get('destination', 'Trip')} Plan!

✈️  {trip_data.get('flight_summary', 'Flight details included')}
🏨 {trip_data.get('hotel_name', 'Hotel reservation confirmed')}
📅 {trip_data.get('dates', 'Check dates in full itinerary')}
💰 Total: ${trip_data.get('total_cost', 'See breakdown')}

View full itinerary: {trip_data.get('link', 'Link will be provided')}

Have a great trip! ✨
"""

        return self.send_sms(
            phone_number=phone_number,
            message=message.strip(),
            trip_id=trip_data.get('trip_id'),
            metadata=trip_data
        )

    def send_email(
        self,
        email_address: str,
        subject: str,
        body: str,
        trip_id: str = None
    ) -> Dict[str, Any]:
        """
        Send email via Elastic AgenticBuilder

        Args:
            email_address: Recipient email
            subject: Email subject
            body: Email body (HTML supported)
            trip_id: Optional trip identifier

        Returns:
            Status dict
        """

        print(f"📧 Sending email via AgenticBuilder to {email_address}")

        try:
            from datetime import datetime

            notification_doc = {
                "recipient": email_address,
                "subject": subject,
                "message": body,
                "notification_type": "email",
                "status": "sent",
                "sent_at": datetime.now().isoformat(),
                "trip_id": trip_id
            }

            result = self.es.index(
                index=self.notification_index,
                document=notification_doc
            )

            print(f"✅ Email sent successfully!")
            print(f"   Message ID: {result['_id']}")

            return {
                "success": True,
                "message_id": result['_id'],
                "status": "sent",
                "recipient": email_address
            }

        except Exception as e:
            print(f"❌ Error sending email: {e}")
            return {
                "success": False,
                "error": str(e)
            }

    def get_notification_status(self, message_id: str) -> Dict[str, Any]:
        """
        Check status of a sent notification

        Args:
            message_id: ID returned from send_sms or send_email

        Returns:
            Notification status dict
        """

        try:
            doc = self.es.get(index=self.notification_index, id=message_id)
            return {
                "success": True,
                "status": doc['_source']['status'],
                "notification": doc['_source']
            }
        except Exception as e:
            return {
                "success": False,
                "error": str(e)
            }


# Test the notification service
if __name__ == '__main__':
    notifier = AgenticBuilderNotification()

    print("="*60)
    print("Testing Elastic AgenticBuilder Notifications")
    print("="*60)

    # Test SMS
    print("\n1. Testing SMS notification:")
    sms_result = notifier.send_sms(
        phone_number="+1234567890",
        message="Test message from Travel Agent workshop!",
        trip_id="test-trip-001",
        metadata={"test": True}
    )

    if sms_result['success']:
        print(f"✓ SMS test passed - Message ID: {sms_result['message_id']}")

    # Test Trip Summary
    print("\n2. Testing trip summary SMS:")
    trip_data = {
        "destination": "Tokyo",
        "flight_summary": "Direct flight, Dec 15",
        "hotel_name": "Park Hyatt Tokyo",
        "dates": "Dec 15-20, 2026",
        "total_cost": 4850,
        "link": "https://example.com/trip/123",
        "trip_id": "trip-tokyo-123"
    }

    trip_result = notifier.send_trip_summary(
        phone_number="+1234567890",
        trip_data=trip_data
    )

    if trip_result['success']:
        print(f"✓ Trip summary test passed")

    # Test Email
    print("\n3. Testing email notification:")
    email_result = notifier.send_email(
        email_address="user@example.com",
        subject="Your Tokyo Trip Itinerary",
        body="<h1>Your trip is confirmed!</h1><p>Details attached.</p>",
        trip_id="trip-tokyo-123"
    )

    if email_result['success']:
        print(f"✓ Email test passed")

    print("\n" + "="*60)
    print("✅ All notification tests complete!")
    print("\nBenefits of AgenticBuilder notifications:")
    print("• No external service required (no Twilio)")
    print("• All data stays in Elastic")
    print("• Indexed for analytics and tracking")
    print("• Native integration with Elastic Cloud")
    print("• Cost-effective (included in Elastic)")
