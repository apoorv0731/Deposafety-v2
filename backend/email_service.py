"""
SendGrid email service integration.
"""
from sendgrid import SendGridAPIClient
from sendgrid.helpers.mail import Mail, Email, To, Content, HtmlContent
from typing import Optional, Dict, Any, List
import logging

from config import get_settings

logger = logging.getLogger(__name__)


class EmailService:
    """SendGrid email service client."""
    
    _instance: Optional['EmailService'] = None
    _client: Optional[SendGridAPIClient] = None
    _from_email: Optional[str] = None
    
    # Email templates
    TEMPLATES = {
        'scan_completed': {
            'subject': 'Your Property Inspection is Complete - DepoSafety',
            'html': '''
            <h2>Inspection Complete</h2>
            <p>Hello {full_name},</p>
            <p>Your property inspection for <strong>{property_name}</strong> has been completed.</p>
            <p><strong>Inspection Details:</strong></p>
            <ul>
                <li>Property: {property_address}</li>
                <li>Inspection Type: {inspection_type}</li>
                <li>Completed: {completed_at}</li>
                <li>Blockchain Verification: {blockchain_tx}</li>
            </ul>
            <p><a href="{scan_url}">View Full Report</a></p>
            <p>Best regards,<br>The DepoSafety Team</p>
            '''
        },
        'scan_processing': {
            'subject': 'Property Inspection Processing - DepoSafety',
            'html': '''
            <h2>Inspection Processing</h2>
            <p>Hello {full_name},</p>
            <p>Your property inspection for <strong>{property_name}</strong> is being processed.</p>
            <p>We are generating your 3D model and blockchain verification. You'll receive another email when complete.</p>
            <p>Best regards,<br>The DepoSafety Team</p>
            '''
        },
        'welcome': {
            'subject': 'Welcome to DepoSafety!',
            'html': '''
            <h2>Welcome to DepoSafety!</h2>
            <p>Hello {full_name},</p>
            <p>Thank you for joining DepoSafety. Your account has been created successfully.</p>
            <p>With DepoSafety, you can:</p>
            <ul>
                <li>Document property conditions with 3D scans</li>
                <li>Secure evidence on the blockchain</li>
                <li>Protect your security deposits</li>
            </ul>
            <p><a href="{dashboard_url}">Get Started</a></p>
            <p>Best regards,<br>The DepoSafety Team</p>
            '''
        },
        'password_reset': {
            'subject': 'Password Reset Request - DepoSafety',
            'html': '''
            <h2>Password Reset</h2>
            <p>Hello,</p>
            <p>You requested a password reset for your DepoSafety account.</p>
            <p><a href="{reset_url}">Click here to reset your password</a></p>
            <p>If you didn't request this, please ignore this email.</p>
            <p>Best regards,<br>The DepoSafety Team</p>
            '''
        }
    }
    
    def __new__(cls):
        if cls._instance is None:
            cls._instance = super().__new__(cls)
        return cls._instance
    
    def __init__(self):
        if self._client is None:
            settings = get_settings()
            self._from_email = settings.from_email
            
            if settings.sendgrid_api_key:
                try:
                    self._client = SendGridAPIClient(settings.sendgrid_api_key)
                    logger.info("SendGrid client initialized")
                except Exception as e:
                    logger.error(f"Failed to initialize SendGrid: {e}")
            else:
                logger.warning("SendGrid API key not configured")
    
    @property
    def is_configured(self) -> bool:
        """Check if email service is configured."""
        return self._client is not None
    
    async def send_email(
        self,
        to_email: str,
        subject: str,
        html_content: str,
        from_email: Optional[str] = None
    ) -> Dict[str, Any]:
        """
        Send a generic email.
        
        Args:
            to_email: Recipient email address
            subject: Email subject
            html_content: HTML email body
            from_email: Sender email (defaults to configured from_email)
            
        Returns:
            Dict with success status and message_id or error
        """
        if not self._client:
            logger.error("SendGrid not configured")
            return {'success': False, 'error': 'Email service not configured'}
        
        try:
            from_addr = from_email or self._from_email
            
            message = Mail(
                from_email=Email(from_addr),
                to_emails=To(to_email),
                subject=subject,
                html_content=HtmlContent(html_content)
            )
            
            response = self._client.send(message)
            
            if response.status_code in [200, 201, 202]:
                logger.info(f"Email sent to {to_email}")
                return {
                    'success': True,
                    'message_id': response.headers.get('X-Message-Id')
                }
            else:
                logger.error(f"Failed to send email: {response.status_code}")
                return {
                    'success': False,
                    'error': f'SendGrid returned {response.status_code}'
                }
                
        except Exception as e:
            logger.error(f"Error sending email: {e}")
            return {'success': False, 'error': str(e)}
    
    async def send_template_email(
        self,
        to_email: str,
        template_name: str,
        template_data: Dict[str, Any],
        from_email: Optional[str] = None
    ) -> Dict[str, Any]:
        """
        Send an email using a predefined template.
        
        Args:
            to_email: Recipient email address
            template_name: Name of the template to use
            template_data: Data to populate template variables
            from_email: Sender email (optional)
            
        Returns:
            Dict with success status
        """
        if template_name not in self.TEMPLATES:
            return {'success': False, 'error': f'Template {template_name} not found'}
        
        template = self.TEMPLATES[template_name]
        html_content = template['html'].format(**template_data)
        
        return await self.send_email(
            to_email=to_email,
            subject=template['subject'],
            html_content=html_content,
            from_email=from_email
        )
    
    async def send_scan_completed(
        self,
        to_email: str,
        full_name: str,
        property_name: str,
        property_address: str,
        inspection_type: str,
        completed_at: str,
        blockchain_tx: str,
        scan_url: str
    ) -> Dict[str, Any]:
        """Send scan completion email."""
        return await self.send_template_email(
            to_email=to_email,
            template_name='scan_completed',
            template_data={
                'full_name': full_name,
                'property_name': property_name,
                'property_address': property_address,
                'inspection_type': inspection_type,
                'completed_at': completed_at,
                'blockchain_tx': blockchain_tx,
                'scan_url': scan_url
            }
        )
    
    async def send_welcome(
        self,
        to_email: str,
        full_name: str,
        dashboard_url: str = "https://app.deposafety.com"
    ) -> Dict[str, Any]:
        """Send welcome email to new users."""
        return await self.send_template_email(
            to_email=to_email,
            template_name='welcome',
            template_data={
                'full_name': full_name,
                'dashboard_url': dashboard_url
            }
        )
    
    async def send_bulk_emails(
        self,
        emails: List[Dict[str, Any]]
    ) -> List[Dict[str, Any]]:
        """
        Send multiple emails in batch.
        
        Args:
            emails: List of email dicts with to_email, subject, html_content
            
        Returns:
            List of results for each email
        """
        results = []
        for email_data in emails:
            result = await self.send_email(
                to_email=email_data['to_email'],
                subject=email_data['subject'],
                html_content=email_data['html_content'],
                from_email=email_data.get('from_email')
            )
            results.append(result)
        return results


# Global email service instance
email_service = EmailService()
