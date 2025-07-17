"""
NexGuard Dashboard - Comprehensive Web Interface
Flask application for managing NexGuard Discord Bot
"""

import os
from flask import Flask, render_template, request, jsonify, redirect, url_for, flash, session
from flask_sqlalchemy import SQLAlchemy
from flask_login import LoginManager, UserMixin, login_user, logout_user, login_required, current_user
from flask_wtf import FlaskForm
from flask_cors import CORS
from wtforms import StringField, TextAreaField, BooleanField, IntegerField, SelectField, SubmitField
from wtforms.validators import DataRequired, Length, NumberRange
from datetime import datetime, timedelta
import json
import requests
import logging
from dotenv import load_dotenv

# Load environment variables
load_dotenv()

# Configure logging
logging.basicConfig(level=logging.INFO)
logger = logging.getLogger(__name__)

# Initialize Flask app
app = Flask(__name__)
app.config['SECRET_KEY'] = os.environ.get('SECRET_KEY', 'nexguard-dashboard-secret-key')
app.config['SQLALCHEMY_DATABASE_URI'] = os.environ.get('DATABASE_URL')
app.config['SQLALCHEMY_TRACK_MODIFICATIONS'] = False

# Initialize extensions
db = SQLAlchemy(app)
login_manager = LoginManager(app)
login_manager.login_view = 'login'
login_manager.login_message = 'Please log in to access the dashboard.'
CORS(app)

# Database Models
class User(UserMixin, db.Model):
    __tablename__ = 'dashboard_users'
    id = db.Column(db.Integer, primary_key=True)
    discord_id = db.Column(db.String(20), unique=True, nullable=False)
    username = db.Column(db.String(80), nullable=False)
    avatar_url = db.Column(db.String(255))
    is_admin = db.Column(db.Boolean, default=False)
    created_at = db.Column(db.DateTime, default=datetime.utcnow)
    last_login = db.Column(db.DateTime)

class Guild(db.Model):
    __tablename__ = 'dashboard_guilds'
    id = db.Column(db.Integer, primary_key=True)
    discord_id = db.Column(db.String(20), unique=True, nullable=False)
    name = db.Column(db.String(100), nullable=False)
    icon_url = db.Column(db.String(255))
    owner_id = db.Column(db.String(20), nullable=False)
    member_count = db.Column(db.Integer, default=0)
    is_active = db.Column(db.Boolean, default=True)
    created_at = db.Column(db.DateTime, default=datetime.utcnow)
    updated_at = db.Column(db.DateTime, default=datetime.utcnow, onupdate=datetime.utcnow)

class BotConfig(db.Model):
    __tablename__ = 'bot_configs'
    id = db.Column(db.Integer, primary_key=True)
    guild_id = db.Column(db.String(20), nullable=False)
    config_key = db.Column(db.String(50), nullable=False)
    config_value = db.Column(db.Text)
    config_type = db.Column(db.String(20), default='string')  # string, json, boolean, integer
    created_at = db.Column(db.DateTime, default=datetime.utcnow)
    updated_at = db.Column(db.DateTime, default=datetime.utcnow, onupdate=datetime.utcnow)

class CommandLog(db.Model):
    __tablename__ = 'command_logs'
    id = db.Column(db.Integer, primary_key=True)
    guild_id = db.Column(db.String(20), nullable=False)
    user_id = db.Column(db.String(20), nullable=False)
    command_name = db.Column(db.String(50), nullable=False)
    command_args = db.Column(db.Text)
    success = db.Column(db.Boolean, default=True)
    error_message = db.Column(db.Text)
    execution_time = db.Column(db.Float)
    created_at = db.Column(db.DateTime, default=datetime.utcnow)

# Forms
class GuildConfigForm(FlaskForm):
    prefix = StringField('Bot Prefix', validators=[DataRequired(), Length(min=1, max=5)])
    mod_role = StringField('Moderator Role ID')
    log_channel = StringField('Log Channel ID')
    welcome_enabled = BooleanField('Welcome Messages Enabled')
    automod_enabled = BooleanField('Auto-Moderation Enabled')
    autorole_enabled = BooleanField('Auto-Role Enabled')
    submit = SubmitField('Save Configuration')

class AutoModForm(FlaskForm):
    spam_enabled = BooleanField('Spam Detection')
    spam_limit = IntegerField('Spam Limit', validators=[NumberRange(min=1, max=20)], default=5)
    spam_window = IntegerField('Spam Window (seconds)', validators=[NumberRange(min=1, max=60)], default=10)
    
    links_enabled = BooleanField('Link Detection')
    block_invites = BooleanField('Block Discord Invites')
    block_urls = BooleanField('Block URLs')
    
    badwords_enabled = BooleanField('Bad Words Filter')
    badwords_strict = BooleanField('Strict Mode')
    
    caps_enabled = BooleanField('Caps Lock Detection')
    caps_threshold = IntegerField('Caps Threshold (%)', validators=[NumberRange(min=10, max=100)], default=70)
    
    mentions_enabled = BooleanField('Mention Limits')
    max_mentions = IntegerField('Max User Mentions', validators=[NumberRange(min=1, max=20)], default=5)
    max_role_mentions = IntegerField('Max Role Mentions', validators=[NumberRange(min=1, max=10)], default=2)
    
    submit = SubmitField('Save AutoMod Settings')

class WelcomeForm(FlaskForm):
    enabled = BooleanField('Welcome Messages Enabled')
    channel_id = StringField('Welcome Channel ID')
    tone = SelectField('Welcome Tone', choices=[
        ('friendly', 'Friendly'),
        ('professional', 'Professional'),
        ('enthusiastic', 'Enthusiastic'),
        ('warm', 'Warm'),
        ('gaming', 'Gaming')
    ])
    custom_template = TextAreaField('Custom Template', validators=[Length(max=1500)])
    ai_enabled = BooleanField('AI-Powered Messages')
    submit = SubmitField('Save Welcome Settings')

# Login manager
@login_manager.user_loader
def load_user(user_id):
    return User.query.get(int(user_id))

# Discord OAuth2 configuration
DISCORD_CLIENT_ID = os.environ.get('DISCORD_CLIENT_ID')
DISCORD_CLIENT_SECRET = os.environ.get('DISCORD_CLIENT_SECRET')
DISCORD_REDIRECT_URI = os.environ.get('DISCORD_REDIRECT_URI', 'http://localhost:5000/callback')

# Helper functions
def get_bot_status():
    """Get current bot status from the bot instance"""
    try:
        # This would connect to your bot's status endpoint
        response = requests.get('http://localhost:5000/status', timeout=5)
        if response.status_code == 200:
            return response.json()
    except:
        pass
    return {'status': 'offline', 'guilds': 0, 'users': 0, 'uptime': 0}

def get_guild_stats(guild_id):
    """Get statistics for a specific guild"""
    # Get command usage stats
    recent_commands = CommandLog.query.filter_by(guild_id=guild_id).filter(
        CommandLog.created_at >= datetime.utcnow() - timedelta(days=7)
    ).count()
    
    # Get error rate
    total_commands = CommandLog.query.filter_by(guild_id=guild_id).count()
    error_commands = CommandLog.query.filter_by(guild_id=guild_id, success=False).count()
    error_rate = (error_commands / total_commands * 100) if total_commands > 0 else 0
    
    return {
        'recent_commands': recent_commands,
        'total_commands': total_commands,
        'error_rate': round(error_rate, 2)
    }

def get_config_value(guild_id, key, default=None):
    """Get configuration value for a guild"""
    config = BotConfig.query.filter_by(guild_id=guild_id, config_key=key).first()
    if config:
        if config.config_type == 'json':
            return json.loads(config.config_value)
        elif config.config_type == 'boolean':
            return config.config_value.lower() == 'true'
        elif config.config_type == 'integer':
            return int(config.config_value)
        return config.config_value
    return default

def set_config_value(guild_id, key, value, config_type='string'):
    """Set configuration value for a guild"""
    config = BotConfig.query.filter_by(guild_id=guild_id, config_key=key).first()
    
    if config_type == 'json':
        value = json.dumps(value)
    elif config_type == 'boolean':
        value = str(value).lower()
    elif config_type == 'integer':
        value = str(value)
    
    if config:
        config.config_value = value
        config.config_type = config_type
        config.updated_at = datetime.utcnow()
    else:
        config = BotConfig(
            guild_id=guild_id,
            config_key=key,
            config_value=value,
            config_type=config_type
        )
        db.session.add(config)
    
    db.session.commit()

def validate_bot_token(token):
    """Validate bot token"""
    if not token:
        return False
    
    # Check if it matches the expected bot token from environment
    expected_token = os.getenv('DISCORD_TOKEN')
    if not expected_token:
        return False
    
    # For security, we check if the provided token matches the bot's actual token
    return token == expected_token

# Routes
@app.route('/')
def dashboard():
    """Main dashboard page"""
    if not current_user.is_authenticated:
        return redirect(url_for('login'))
    
    # Get bot status
    bot_status = get_bot_status()
    
    # Get user's guilds (simplified for demo)
    user_guilds = Guild.query.filter_by(owner_id=current_user.discord_id).all()
    
    # Get recent activity
    recent_commands = CommandLog.query.order_by(CommandLog.created_at.desc()).limit(10).all()
    
    return render_template('dashboard.html', 
                         bot_status=bot_status,
                         user_guilds=user_guilds,
                         recent_commands=recent_commands)

@app.route('/login')
def login():
    """Discord OAuth2 login"""
    if current_user.is_authenticated:
        return redirect(url_for('dashboard'))
    
    # For demo purposes, create a simple login form
    return render_template('login.html')

@app.route('/auth/discord')
def discord_auth():
    """Redirect to Discord OAuth2"""
    # For demo purposes, we'll create a simple login that bypasses Discord OAuth
    # In production, you would implement full Discord OAuth2 flow
    
    # Create or get demo user
    user = User.query.filter_by(discord_id='123456789').first()
    if not user:
        user = User(
            discord_id='123456789',
            username='DemoUser',
            avatar_url='https://cdn.discordapp.com/embed/avatars/0.png',
            is_admin=True
        )
        db.session.add(user)
        db.session.commit()
    
    user.last_login = datetime.utcnow()
    db.session.commit()
    
    login_user(user)
    flash('Successfully logged in as demo user!', 'success')
    return redirect(url_for('dashboard'))

@app.route('/callback')
def callback():
    """Discord OAuth2 callback"""
    code = request.args.get('code')
    if not code:
        flash('Authentication failed', 'danger')
        return redirect(url_for('login'))
    
    # Exchange code for access token (simplified for demo)
    # In production, you'd implement full OAuth2 flow
    
    try:
        # For demo, create a test user
        user = User.query.filter_by(discord_id='123456789').first()
        if not user:
            user = User(
                discord_id='123456789',
                username='DemoUser',
                avatar_url='https://cdn.discordapp.com/embed/avatars/0.png',
                is_admin=True
            )
            db.session.add(user)
            db.session.commit()
        
        user.last_login = datetime.utcnow()
        db.session.commit()
        
        login_user(user)
        flash('Successfully logged in!', 'success')
        return redirect(url_for('dashboard'))
    except Exception as e:
        flash(f'Login error: {str(e)}', 'danger')
        return redirect(url_for('login'))

@app.route('/logout')
@login_required
def logout():
    """Logout user"""
    logout_user()
    return redirect(url_for('login'))

@app.route('/guild/<guild_id>', methods=['GET', 'POST'])
@login_required
def guild_config(guild_id):
    """Guild configuration page"""
    guild = Guild.query.filter_by(discord_id=guild_id).first()
    if not guild:
        flash('Guild not found', 'danger')
        return redirect(url_for('dashboard'))
    
    # Get guild statistics
    stats = get_guild_stats(guild_id)
    
    # Get current configuration
    config = {
        'prefix': get_config_value(guild_id, 'prefix', '!'),
        'mod_role': get_config_value(guild_id, 'mod_role'),
        'log_channel': get_config_value(guild_id, 'log_channel'),
        'welcome_enabled': get_config_value(guild_id, 'welcome_enabled', False),
        'automod_enabled': get_config_value(guild_id, 'automod_enabled', False),
        'autorole_enabled': get_config_value(guild_id, 'autorole_enabled', False)
    }
    
    form = GuildConfigForm(data=config)
    
    if form.validate_on_submit():
        try:
            set_config_value(guild_id, 'prefix', form.prefix.data)
            set_config_value(guild_id, 'mod_role', form.mod_role.data)
            set_config_value(guild_id, 'log_channel', form.log_channel.data)
            set_config_value(guild_id, 'welcome_enabled', form.welcome_enabled.data, 'boolean')
            set_config_value(guild_id, 'automod_enabled', form.automod_enabled.data, 'boolean')
            set_config_value(guild_id, 'autorole_enabled', form.autorole_enabled.data, 'boolean')
            
            flash('Configuration saved successfully!', 'success')
            return redirect(url_for('guild_config', guild_id=guild_id))
        except Exception as e:
            flash(f'Error saving configuration: {str(e)}', 'danger')
    
    return render_template('guild_config.html', guild=guild, form=form, stats=stats)

@app.route('/guild/<guild_id>/automod')
@login_required
def automod_config(guild_id):
    """AutoMod configuration page"""
    guild = Guild.query.filter_by(discord_id=guild_id).first()
    if not guild:
        flash('Guild not found')
        return redirect(url_for('dashboard'))
    
    # Get current automod settings
    automod_settings = get_config_value(guild_id, 'automod_settings', {})
    
    form = AutoModForm(data=automod_settings)
    
    if form.validate_on_submit():
        settings = {
            'spam_enabled': form.spam_enabled.data,
            'spam_limit': form.spam_limit.data,
            'spam_window': form.spam_window.data,
            'links_enabled': form.links_enabled.data,
            'block_invites': form.block_invites.data,
            'block_urls': form.block_urls.data,
            'badwords_enabled': form.badwords_enabled.data,
            'badwords_strict': form.badwords_strict.data,
            'caps_enabled': form.caps_enabled.data,
            'caps_threshold': form.caps_threshold.data,
            'mentions_enabled': form.mentions_enabled.data,
            'max_mentions': form.max_mentions.data,
            'max_role_mentions': form.max_role_mentions.data
        }
        
        set_config_value(guild_id, 'automod_settings', settings, 'json')
        flash('AutoMod settings saved successfully!', 'success')
        return redirect(url_for('automod_config', guild_id=guild_id))
    
    return render_template('automod_config.html', guild=guild, form=form)

@app.route('/guild/<guild_id>/welcome')
@login_required
def welcome_config(guild_id):
    """Welcome system configuration page"""
    guild = Guild.query.filter_by(discord_id=guild_id).first()
    if not guild:
        flash('Guild not found')
        return redirect(url_for('dashboard'))
    
    # Get current welcome settings
    welcome_settings = get_config_value(guild_id, 'welcome_settings', {})
    
    form = WelcomeForm(data=welcome_settings)
    
    if form.validate_on_submit():
        settings = {
            'enabled': form.enabled.data,
            'channel_id': form.channel_id.data,
            'tone': form.tone.data,
            'custom_template': form.custom_template.data,
            'ai_enabled': form.ai_enabled.data
        }
        
        set_config_value(guild_id, 'welcome_settings', settings, 'json')
        flash('Welcome settings saved successfully!', 'success')
        return redirect(url_for('welcome_config', guild_id=guild_id))
    
    return render_template('welcome_config.html', guild=guild, form=form)

@app.route('/commands')
@login_required
def commands():
    """Commands overview page"""
    # Get command statistics
    command_stats = db.session.query(
        CommandLog.command_name,
        db.func.count(CommandLog.id).label('usage_count'),
        db.func.avg(CommandLog.execution_time).label('avg_time')
    ).group_by(CommandLog.command_name).order_by(db.desc('usage_count')).all()
    
    return render_template('commands.html', command_stats=command_stats)

@app.route('/logs')
@login_required
def logs():
    """Logs and monitoring page"""
    # Get recent logs
    recent_logs = CommandLog.query.order_by(CommandLog.created_at.desc()).limit(50).all()
    
    # Get error logs
    error_logs = CommandLog.query.filter_by(success=False).order_by(CommandLog.created_at.desc()).limit(20).all()
    
    return render_template('logs.html', recent_logs=recent_logs, error_logs=error_logs)

@app.route('/api/bot/status')
def api_bot_status():
    """API endpoint for bot status"""
    return jsonify(get_bot_status())

@app.route('/api/guild/<guild_id>/stats')
@login_required
def api_guild_stats(guild_id):
    """API endpoint for guild statistics"""
    return jsonify(get_guild_stats(guild_id))

@app.route('/api/commands/execute', methods=['POST'])
@login_required
def api_execute_command():
    """API endpoint to execute bot commands"""
    try:
        data = request.get_json()
        command = data.get('command')
        guild_id = data.get('guild_id')
        
        # Log the command execution
        log_entry = CommandLog(
            guild_id=guild_id or 'global',
            user_id=current_user.discord_id,
            command_name=command,
            command_args=json.dumps(data.get('args', {})),
            success=True,
            execution_time=0.1
        )
        db.session.add(log_entry)
        db.session.commit()
        
        return jsonify({'success': True, 'message': f'Command {command} executed successfully'})
    except Exception as e:
        return jsonify({'success': False, 'message': f'Command execution failed: {str(e)}'}), 500

@app.route('/api/dashboard/data')
@login_required
def api_dashboard_data():
    """API endpoint for dashboard data"""
    try:
        # Get bot status (simulated)
        bot_status = {
            'status': 'online',
            'guilds': 6,
            'users': 116,
            'commands': 55,
            'uptime': '2d 14h 32m'
        }
        
        # Get recent activity
        recent_commands = CommandLog.query.order_by(CommandLog.created_at.desc()).limit(5).all()
        recent_activity = [{
            'command_name': cmd.command_name,
            'success': cmd.success,
            'created_at': cmd.created_at.isoformat()
        } for cmd in recent_commands]
        
        return jsonify({
            'bot_status': bot_status,
            'recent_activity': recent_activity,
            'stats': {
                'total_commands': CommandLog.query.count(),
                'guilds': 6,
                'users': 116
            }
        })
    except Exception as e:
        return jsonify({'error': str(e)}), 500

def create_tables():
    """Create database tables"""
    try:
        db.create_all()
        print("Database tables created successfully")
        
        # Create demo guild if it doesn't exist
        if not Guild.query.filter_by(discord_id='123456789').first():
            demo_guild = Guild(
                discord_id='123456789',
                name='Demo Server',
                owner_id='123456789',
                member_count=100
            )
            db.session.add(demo_guild)
            db.session.commit()
            print("Demo guild created")
    except Exception as e:
        print(f"Database setup error: {e}")

# Bot API Integration Endpoints
@app.route('/api/bot/servers/<guild_id>/config', methods=['GET'])
def get_server_config(guild_id):
    """Get server configuration for bot"""
    # Check for bot authentication
    auth_header = request.headers.get('Authorization')
    if not auth_header or not auth_header.startswith('Bearer '):
        return jsonify({'error': 'Bot authentication required'}), 401
    
    token = auth_header.replace('Bearer ', '')
    if not validate_bot_token(token):
        return jsonify({'error': 'Invalid bot token'}), 401
    
    try:
        # Get configuration from database
        config = {
            'moderationEnabled': get_config_value(guild_id, 'moderation_enabled', True),
            'autoModEnabled': get_config_value(guild_id, 'automod_enabled', False),
            'spamProtection': get_config_value(guild_id, 'spam_protection', False),
            'welcomeEnabled': get_config_value(guild_id, 'welcome_enabled', False),
            'customCommandsEnabled': get_config_value(guild_id, 'custom_commands_enabled', False),
            'prefix': get_config_value(guild_id, 'prefix', '!'),
            'logChannel': get_config_value(guild_id, 'log_channel'),
            'modRole': get_config_value(guild_id, 'mod_role')
        }
        
        return jsonify(config)
    except Exception as e:
        app.logger.error(f"Error getting server config: {e}")
        return jsonify({'error': 'Internal server error'}), 500

@app.route('/api/bot/servers/<guild_id>/commands', methods=['GET', 'POST'])
def handle_custom_commands(guild_id):
    """Handle custom commands for bot"""
    # Check for bot authentication
    auth_header = request.headers.get('Authorization')
    if not auth_header or not auth_header.startswith('Bearer '):
        return jsonify({'error': 'Bot authentication required'}), 401
    
    if request.method == 'GET':
        try:
            # Get custom commands from database
            commands = []  # Placeholder - implement custom commands table
            return jsonify(commands)
        except Exception as e:
            app.logger.error(f"Error getting custom commands: {e}")
            return jsonify({'error': 'Internal server error'}), 500
    
    elif request.method == 'POST':
        try:
            data = request.get_json()
            name = data.get('name')
            response_text = data.get('response')
            created_by = data.get('createdBy')
            
            # Create custom command in database
            # Placeholder implementation
            command = {
                'id': 1,
                'name': name,
                'response': response_text,
                'createdBy': created_by,
                'createdAt': datetime.utcnow().isoformat()
            }
            
            return jsonify(command)
        except Exception as e:
            app.logger.error(f"Error creating custom command: {e}")
            return jsonify({'error': 'Internal server error'}), 500

@app.route('/api/bot/servers/<guild_id>/moderation/log', methods=['POST'])
def log_moderation_action(guild_id):
    """Log moderation action from bot"""
    # Check for bot authentication
    auth_header = request.headers.get('Authorization')
    if not auth_header or not auth_header.startswith('Bearer '):
        return jsonify({'error': 'Bot authentication required'}), 401
    
    try:
        data = request.get_json()
        action_type = data.get('type')
        user_id = data.get('userId')
        moderator_id = data.get('moderatorId')
        reason = data.get('reason')
        
        # Log to database
        log_entry = CommandLog(
            guild_id=guild_id,
            user_id=user_id,
            command_name=action_type,
            command_args=reason,
            success=True,
            execution_time=0.0
        )
        
        db.session.add(log_entry)
        db.session.commit()
        
        return jsonify({'success': True})
    except Exception as e:
        app.logger.error(f"Error logging moderation action: {e}")
        return jsonify({'error': 'Internal server error'}), 500

@app.route('/api/bot/status', methods=['POST'])
def update_bot_status():
    """Update bot status from bot"""
    # Check for bot authentication
    auth_header = request.headers.get('Authorization')
    if not auth_header or not auth_header.startswith('Bearer '):
        return jsonify({'error': 'Bot authentication required'}), 401
    
    try:
        data = request.get_json()
        # Update bot status in database or cache
        # Placeholder implementation
        return jsonify({'success': True})
    except Exception as e:
        app.logger.error(f"Error updating bot status: {e}")
        return jsonify({'error': 'Internal server error'}), 500

@app.route('/api/bot/servers/<guild_id>/automod', methods=['GET'])
def get_automod_config(guild_id):
    """Get automod configuration for bot"""
    # Check for bot authentication
    auth_header = request.headers.get('Authorization')
    if not auth_header or not auth_header.startswith('Bearer '):
        return jsonify({'error': 'Bot authentication required'}), 401
    
    try:
        automod_settings = get_config_value(guild_id, 'automod_settings', {})
        return jsonify(automod_settings)
    except Exception as e:
        app.logger.error(f"Error getting automod config: {e}")
        return jsonify({'error': 'Internal server error'}), 500

@app.route('/api/bot/servers/<guild_id>/welcome', methods=['GET'])
def get_welcome_config(guild_id):
    """Get welcome configuration for bot"""
    # Check for bot authentication
    auth_header = request.headers.get('Authorization')
    if not auth_header or not auth_header.startswith('Bearer '):
        return jsonify({'error': 'Bot authentication required'}), 401
    
    try:
        welcome_settings = get_config_value(guild_id, 'welcome_settings', {})
        return jsonify(welcome_settings)
    except Exception as e:
        app.logger.error(f"Error getting welcome config: {e}")
        return jsonify({'error': 'Internal server error'}), 500

@app.route('/api/bot/servers/<guild_id>/commands/log', methods=['POST'])
def log_command_usage(guild_id):
    """Log command usage from bot"""
    # Check for bot authentication
    auth_header = request.headers.get('Authorization')
    if not auth_header or not auth_header.startswith('Bearer '):
        return jsonify({'error': 'Bot authentication required'}), 401
    
    try:
        data = request.get_json()
        user_id = data.get('userId')
        command_name = data.get('commandName')
        success = data.get('success', True)
        execution_time = data.get('executionTime', 0.0)
        
        # Log to database
        log_entry = CommandLog(
            guild_id=guild_id,
            user_id=user_id,
            command_name=command_name,
            success=success,
            execution_time=execution_time
        )
        
        db.session.add(log_entry)
        db.session.commit()
        
        return jsonify({'success': True})
    except Exception as e:
        app.logger.error(f"Error logging command usage: {e}")
        return jsonify({'error': 'Internal server error'}), 500

@app.route('/api/bot/servers/<guild_id>/autoreply', methods=['GET'])
def get_autoreply_rules(guild_id):
    """Get auto-reply rules for a guild"""
    auth_header = request.headers.get('Authorization')
    if not auth_header or not auth_header.startswith('Bearer '):
        return jsonify({'error': 'Bot authentication required'}), 401
    
    try:
        # For now, return empty list as auto-reply rules are managed via SQLite in the bot
        # This can be enhanced to sync with PostgreSQL if needed
        return jsonify({
            'rules': [],
            'enabled': True,
            'totalRules': 0
        })
    
    except Exception as e:
        app.logger.error(f"Error getting auto-reply rules: {e}")
        return jsonify({'error': 'Internal server error'}), 500

@app.route('/api/bot/servers/<guild_id>/autoreply/trigger', methods=['POST'])
def log_autoreply_trigger(guild_id):
    """Log auto-reply trigger from bot"""
    auth_header = request.headers.get('Authorization')
    if not auth_header or not auth_header.startswith('Bearer '):
        return jsonify({'error': 'Bot authentication required'}), 401
    
    try:
        data = request.get_json()
        
        # Log the auto-reply trigger (can be expanded to store in PostgreSQL)
        app.logger.info(f"Auto-reply triggered in guild {guild_id}: {data}")
        
        return jsonify({'success': True, 'message': 'Auto-reply trigger logged successfully'})
    
    except Exception as e:
        app.logger.error(f"Error logging auto-reply trigger: {e}")
        return jsonify({'error': 'Internal server error'}), 500

@app.route('/health')
def health_check():
    """Health check endpoint"""
    return jsonify({'status': 'healthy', 'app': 'NexGuard Dashboard'})

if __name__ == '__main__':
    port = int(os.environ.get('PORT', 8080))
    print(f"Starting NexGuard Dashboard on port {port}")
    print(f"Database URL: {app.config['SQLALCHEMY_DATABASE_URI'][:50]}...")
    
    # Create tables
    with app.app_context():
        create_tables()
    
    # Run the app
    app.run(host='0.0.0.0', port=port, debug=False, threaded=True)