import nodemailer from 'nodemailer';

interface EmailParams {
  to: string;
  subject: string;
  html: string;
  text?: string;
}

class EmailService {
  private transporter: nodemailer.Transporter | null = null;

  constructor() {
    this.initializeTransporter();
  }

  private initializeTransporter() {
    if (!process.env.GMAIL_APP_PASSWORD) {
      console.warn('Gmail App Password not configured - email notifications disabled');
      return;
    }

    this.transporter = nodemailer.createTransport({
      service: 'gmail',
      auth: {
        user: 'nexguards@gmail.com',
        pass: process.env.GMAIL_APP_PASSWORD
      }
    });
  }

  async sendEmail(params: EmailParams): Promise<boolean> {
    if (!this.transporter) {
      console.error('Email service not configured');
      return false;
    }

    try {
      const mailOptions = {
        from: 'nexguards@gmail.com',
        to: params.to,
        subject: params.subject,
        html: params.html,
        text: params.text
      };

      const result = await this.transporter.sendMail(mailOptions);
      console.log(`Email sent successfully: ${result.messageId}`);
      return true;
    } catch (error) {
      console.error('Failed to send email:', error);
      return false;
    }
  }

  async sendTestimonialNotification(testimonial: {
    name: string;
    rating: number;
    message: string;
    email?: string;
  }): Promise<boolean> {
    const subject = `New Testimonial Submitted - ${testimonial.rating}⭐ from ${testimonial.name}`;
    
    const html = `
      <div style="font-family: Arial, sans-serif; max-width: 600px; margin: 0 auto;">
        <h2 style="color: #00FFFF; border-bottom: 2px solid #00FFFF; padding-bottom: 10px;">
          🛡️ New NexGuard Testimonial
        </h2>
        
        <div style="background: #f9f9f9; padding: 20px; border-radius: 8px; margin: 20px 0;">
          <h3 style="color: #333; margin-top: 0;">Testimonial Details</h3>
          <p><strong>Name:</strong> ${testimonial.name}</p>
          <p><strong>Rating:</strong> ${testimonial.rating}/5 ⭐</p>
          ${testimonial.email ? `<p><strong>Email:</strong> ${testimonial.email}</p>` : ''}
          
          <div style="margin-top: 20px;">
            <strong>Message:</strong>
            <div style="background: white; padding: 15px; border-left: 4px solid #00FFFF; margin-top: 10px;">
              ${testimonial.message}
            </div>
          </div>
        </div>
        
        <p style="color: #666; font-size: 12px;">
          This testimonial was submitted through the NexGuard website and is pending approval.
        </p>
      </div>
    `;

    return this.sendEmail({
      to: 'nexguards@gmail.com',
      subject,
      html
    });
  }

  async sendFeedbackNotification(feedback: {
    name: string;
    email?: string;
    type: string;
    message: string;
  }): Promise<boolean> {
    const subject = `New Feedback: ${feedback.type} from ${feedback.name}`;
    
    const html = `
      <div style="font-family: Arial, sans-serif; max-width: 600px; margin: 0 auto;">
        <h2 style="color: #00FFFF; border-bottom: 2px solid #00FFFF; padding-bottom: 10px;">
          📝 New NexGuard Feedback
        </h2>
        
        <div style="background: #f9f9f9; padding: 20px; border-radius: 8px; margin: 20px 0;">
          <h3 style="color: #333; margin-top: 0;">Feedback Details</h3>
          <p><strong>Name:</strong> ${feedback.name}</p>
          ${feedback.email ? `<p><strong>Email:</strong> ${feedback.email}</p>` : ''}
          <p><strong>Type:</strong> ${feedback.type}</p>
          
          <div style="margin-top: 20px;">
            <strong>Message:</strong>
            <div style="background: white; padding: 15px; border-left: 4px solid #00FFFF; margin-top: 10px;">
              ${feedback.message}
            </div>
          </div>
        </div>
        
        <p style="color: #666; font-size: 12px;">
          This feedback was submitted through the NexGuard website feedback system.
        </p>
      </div>
    `;

    return this.sendEmail({
      to: 'nexguards@gmail.com',
      subject,
      html
    });
  }
}

export const emailService = new EmailService();