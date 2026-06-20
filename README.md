# Telegram Giveaway Bot

A professional Telegram bot for running giveaways and contests in channels with advanced features including automatic participant collection, scheduled publishing, and broadcast capabilities.

## Features

### Core Functionality

- **Giveaway Creation**: Create customizable giveaways with rich text and custom buttons
- **Multiple Participation Modes**: 
  - Manual (users click to participate)
  - Automatic (scans all channel members)
- **Channel Subscription Requirements**: Require users to subscribe to multiple channels
- **Scheduled Publishing**: Plan giveaways for future publication
- **Flexible Ending Conditions**: End by time or participant count
- **Winner Selection**: Random winner selection with configurable count
- **Admin Panel**: Full management interface through Telegram

### Advanced Features

- **Participant Management**: Add/remove participants manually
- **Live Editing**: Edit active giveaways (text, winners count, button text, end time)
- **Broadcast System**: Send giveaway notifications to all channel members
- **Telethon Integration**: Automated participant scanning using Telegram API
- **Multi-Channel Support**: Manage multiple channels from one bot
- **Timezone Support**: Configurable timezone for scheduling

### Smart Management

- **Real-time Statistics**: Track participant count in real-time
- **Subscription Verification**: Auto-check channel subscriptions before participation
- **Admin-Only Access**: Secure admin panel with user ID verification
- **Session Management**: Persistent Telegram sessions for automation

## Requirements

- Python 3.8+
- Telegram Bot Token
- SQLite (included with Python)
- (Optional) Telegram API credentials for automatic features

## Installation

1. **Clone the repository:**

```bash
git clone https://github.com/fedyaqq34356/Random-bot.git
cd Random-bot
```

2. **Create virtual environment:**

```bash
python -m venv venv
```

3. **Activate virtual environment:**

**Windows:**
```bash
venv\Scripts\activate
```

**macOS/Linux:**
```bash
source venv/bin/activate
```

4. **Install dependencies:**

```bash
pip install -r requirements.txt
```

## Configuration

### 1. Environment Variables

Create a `.env` file in the project root:

```env
BOT_TOKEN=your_telegram_bot_token_here
ADMIN_IDS=123456789,987654321
CARD_NUMBER=5168742012345678
```

**Getting Bot Token:**
1. Message [@BotFather](https://t.me/BotFather) on Telegram
2. Send `/newbot` command
3. Follow instructions to create your bot
4. Copy the token to `.env` file

**Admin IDs:**
- Get your Telegram user ID from [@userinfobot](https://t.me/userinfobot)
- Add multiple admin IDs separated by commas

### 2. Timezone Configuration

Edit `config.py` to set your timezone:

```python
TIMEZONE: str = "Europe/Amsterdam"  # Change to your timezone
GMT_OFFSET: str = "GMT+1"           # Change to match your timezone
```

Common timezones:
- `"America/New_York"` - Eastern Time
- `"Europe/London"` - GMT/BST
- `"Asia/Tokyo"` - Japan Standard Time
- `"Australia/Sydney"` - Australian Eastern Time

### 3. Telegram API Credentials (Optional)

For automatic participant scanning and broadcasting, you'll need:

1. Visit https://my.telegram.org/auth
2. Log in with your phone number
3. Go to "API development tools"
4. Create an application
5. Save your `api_id` and `api_hash`

**Note:** You'll enter these through the bot interface when using automatic features.

## Database Structure

The bot automatically creates an SQLite database with three tables:

### Giveaways Table
- Stores all giveaway information
- Tracks status (draft, published, finished)
- Manages end conditions and winner counts

### Participants Table
- Records all giveaway participants
- Links users to specific giveaways
- Prevents duplicate entries

### Admin Channels Table
- Saves admin's channel list
- Speeds up channel selection

## Usage

### Starting the Bot

Run the main script:

```bash
python main.py
```

Console output:
```
2026-02-12 20:06:27 [INFO] bot: Бот запущен
```

### Bot Commands

**For Admins:**
- `/start` - Open main menu

**Main Menu Options:**
- 🎯 **Create Giveaway** - Start new giveaway
- 📋 **My Giveaways** - View all your giveaways
- 📺 **My Channels** - List saved channels
- 👥 **Manage Participants** - Add/remove participants
- ✏️ **Edit Giveaway** - Modify active giveaways
- 📢 **Broadcast** - Send notifications to channel members

**For Regular Users:**
- `/start` - View bot information and donation details

## Creating a Giveaway

### Step-by-Step Guide

1. **Start Creation**
   - Click "Create Giveaway" in main menu
   - Send giveaway text (supports Telegram formatting)

2. **Button Text**
   - Choose from presets or send custom text
   - Preset options: "Участвую!", "Участвовать", "Принять участие"

3. **Participation Mode**
   - 🔘 **Manual**: Users click button to participate
   - ⚡️ **Automatic**: All channel members added automatically (requires auth)

4. **Main Channel**
   - Send channel @username or forward a message from the channel
   - Bot must be admin in the channel
   - You must be admin in the channel

5. **Additional Channels (Optional)**
   - Add channels for required subscriptions
   - Send @username or forward message
   - Provide subscription link for each channel
   - Bot must be admin in all channels

6. **Winners Count**
   - Enter number of winners (minimum 1)

7. **Publishing Time**
   - ⏰ **Now**: Publish immediately
   - 📅 **Schedule**: Set future date and time (format: `dd.mm.yyyy hh:mm`)

8. **End Condition**
   - ⏱ **By Time**: Set end date and time
   - 👥 **By Participant Count**: Set target participant number

9. **Authorization (Automatic Mode Only)**
   - Enter API ID and API Hash
   - Enter phone number
   - Enter verification code
   - (If enabled) Enter 2FA password

### Example Giveaway Flow

```
You: /start
Bot: ✋ Приветствуем!
     [Create Giveaway]

You: [Create Giveaway]
Bot: Создание розыгрыша:
     ✉️ Отправьте текст для розыгрыша.

You: 🎁 Win a free iPhone 15!
     Participate for a chance to win!
Bot: ✅ Текст добавлен
     ✉️ Отправьте текст кнопки или выберите вариант:
     [Участвую!] [Участвовать] [Принять участие]

You: [Участвую!]
Bot: ✅ Текст кнопки сохранен
     👥 Выберите режим участия:
     [Manual] [Automatic]

You: [Manual]
Bot: ✅ Выбран ручной режим
     📢 В каком канале публикуем розыгрыш?

You: @mychannel
Bot: ✅ Канал выбран: @mychannel
     ➕ Добавьте каналы для обязательной подписки (необязательно).

You: [Continue with 1 subscription]
Bot: ✅ Продолжаем с 1 обязательными подписками
     🏆 Сколько победителей?

You: 3
Bot: ✅ Победителей: 3
     ⏳ Когда публиковать розыгрыш?
     [Now] [Schedule]

You: [Now]
Bot: ✅ Публикуем сразу
     ✍️ Как завершить розыгрыш?
     [By Time] [By Participant Count]

You: [By Time]
Bot: ⏰ Когда завершить? (дд.мм.гггг чч:мм)

You: 15.03.2026 18:00
Bot: ✅ Завершение: 15.03.2026 18:00
     ✅ Розыгрыш создан и опубликован!
```

## Managing Giveaways

### Participant Management

**View Participants:**
1. Main Menu → Manage Participants
2. Select giveaway
3. Click "View Participants"
4. Navigate with ◀️ ▶️ buttons

**Add Participant:**
1. Main Menu → Manage Participants
2. Select giveaway
3. Click "Add Participant"
4. Send user ID or @username

**Remove Participant:**
1. Main Menu → Manage Participants
2. Select giveaway
3. Click "Remove Participant"
4. Click ❌ next to username

### Editing Giveaways

**Edit Text:**
1. Main Menu → Edit Giveaway
2. Select giveaway
3. Click "Change Text"
4. Send new text
5. ✅ Channel message updated automatically

**Edit Winners Count:**
1. Main Menu → Edit Giveaway
2. Select giveaway
3. Click "Winners Count"
4. Send new number

**Edit Button Text:**
1. Main Menu → Edit Giveaway
2. Select giveaway
3. Click "Button Text"
4. Send new text
5. ✅ Channel message updated automatically

**Edit End Time:**
1. Main Menu → Edit Giveaway
2. Select giveaway
3. Click "End Time"
4. Send new date/time (only for time-based giveaways)

### Broadcasting

Send giveaway notifications to all channel members:

1. Main Menu → Broadcast
2. Select giveaway
3. Authorize your Telegram account (if not already)
4. Confirm broadcast start
5. Wait for completion (includes delays to prevent flood)

**Broadcast Message Format:**
```
🎉 Привет! В канале проходит розыгрыш!

Нажмите кнопку «Участвовать» чтобы принять участие:
[Link to giveaway message]
```

## Project Structure

```
Random-bot/
├── main.py                       # Entry point, polling, schedulers
├── config.py                     # Configuration and environment
├── database.py                   # SQLite database manager
├── logger.py                     # Logging configuration
├── bot.log                       # Log file
├── requirements.txt              # Python dependencies
├── .env                          # Environment variables (create this)
├── .gitignore                   # Git ignore rules
├── giveaway.db                   # SQLite database (auto-generated)
│
├── handlers/                     # Bot command handlers
│   ├── __init__.py
│   ├── start.py                 # /start command, main menu
│   ├── giveaway_create.py       # Giveaway creation flow
│   ├── giveaway_participate.py  # User participation handler
│   ├── giveaway_manage.py       # Participant management
│   ├── giveaway_edit.py         # Giveaway editing
│   └── telethon_handler.py      # Telethon auth & operations
│
├── keyboards/                    # Inline keyboard layouts
│   ├── __init__.py
│   └── inline.py                # All inline keyboards
│
├── services/                     # External integrations
│   ├── devices.py               # Random device generation
│   ├── telethon_auth.py         # Telethon authentication
│   └── telethon_scanner.py      # Participant scanning & broadcast
│
├── states/                       # FSM states
│   ├── __init__.py
│   └── giveaway.py              # All bot states
│
├── utils/                        # Utility functions
│   ├── __init__.py
│   ├── channel_utils.py         # Channel verification functions
│   └── time_utils.py            # Time parsing and formatting
│
└── sessions/                     # Telethon sessions (auto-generated)
    └── [user_id].session
```

## How It Works

### Architecture

1. **Main Layer** (`main.py`)
   - Initializes bot and dispatcher
   - Manages background schedulers
   - Handles polling

2. **Handler Layer** (`handlers/`)
   - Processes user commands
   - Manages conversation flows
   - Coordinates between components

3. **Service Layer** (`services/`)
   - Telethon integration
   - Participant scanning
   - Broadcast system

4. **Data Layer** (`database.py`)
   - SQLite operations
   - Data persistence
   - Query management

### Background Tasks

**Time-based Giveaway Checker:**
- Runs every 30 seconds
- Checks for expired giveaways
- Automatically finishes and announces winners

**Scheduled Publishing Checker:**
- Runs every 30 seconds
- Publishes scheduled giveaways
- Updates giveaway status

### Participation Flow

```
User clicks "Participate" button
    ↓
Bot checks subscription to all required channels
    ↓
    ├─ Not subscribed → Show subscription links
    │                   Reject participation
    └─ Subscribed → Add to participants
                    Check end condition
                    ├─ Participant count reached → Finish giveaway
                    └─ Continue → Update counter
```

### Winner Selection Algorithm

```python
if participants_count < winners_count:
    winners = all_participants
else:
    winners = random.sample(participants, winners_count)
```

### Telethon Integration

**Authentication:**
1. User provides API credentials
2. Bot creates Telethon client with random device info
3. Sends verification code
4. User confirms with code (and 2FA if needed)
5. Session saved for future use

**Participant Scanning:**
1. Fetch channel entity
2. Get admin list (exclude from participants)
3. Iterate through channel members (200 at a time)
4. Filter out bots, deleted accounts, and admins
5. Add to database

**Broadcasting:**
1. Fetch channel members
2. Send personalized messages
3. Implement 2-second delays between messages
4. Handle FloodWait errors
5. Skip blocked/private users

## Logging

Logs are saved to `bot.log` with rotation (5MB max, 3 backups):

```
2026-02-12 20:06:27 [INFO] bot: Бот запущен
2026-02-12 20:09:32 [INFO] bot: Код отправлен для user_id=1205595267
2026-02-12 20:09:53 [INFO] bot: Розыгрыш 1: добавлено 2 участников из канала -1003799497486
```

Log levels:
- **INFO**: Normal operations
- **WARNING**: Non-critical issues
- **ERROR**: Errors and exceptions

## Troubleshooting

### Common Issues

**Issue:** "Бот не является администратором канала"

**Solution:** 
1. Add bot to channel
2. Promote to administrator
3. Grant "Post messages" permission
4. Try again

---

**Issue:** "Сессия не найдена" during automatic mode

**Solution:**
1. Complete authorization process
2. Don't close bot during auth
3. If persists, restart from beginning

---

**Issue:** Scheduled giveaway not publishing

**Solution:**
1. Check timezone configuration in `config.py`
2. Verify time is in the future
3. Check bot logs for errors
4. Ensure bot is running continuously

---

**Issue:** "FloodWait" errors during broadcast

**Solution:**
- This is normal Telegram rate limiting
- Bot automatically handles delays
- Wait for broadcast to complete
- Don't send too many broadcasts in short time

---

**Issue:** Users can't participate despite being subscribed

**Solution:**
1. Verify bot has admin rights in all required channels
2. Check channel IDs are correct
3. Ensure subscription links are valid
4. Test with a different user account

---

**Issue:** Database locked error

**Solution:**
1. Only run one bot instance
2. Close other connections to the database
3. Restart the bot

## Security Considerations

- **Environment Variables:** Never commit `.env` to version control
- **Session Files:** Keep `sessions/` directory private
- **Admin IDs:** Only trust verified admin user IDs
- **API Credentials:** Store securely, rotate periodically
- **Rate Limiting:** Bot implements automatic delays
- **Subscription Checks:** Always verify before participation
- **Database:** SQLite file permissions should be restricted

## Performance

### Specifications

- **Participant Scanning:** ~200 users per request
- **Broadcast Speed:** ~1800 messages/hour (2s delay)
- **Database:** SQLite (suitable for < 100K participants)
- **Concurrent Users:** Handles multiple admins simultaneously
- **Memory Usage:** Low (~50-100MB typical)

### Optimization Tips

1. **For Large Channels (10K+ members):**
   - Increase scanning limits in `telethon_scanner.py`
   - Use dedicated VPS for stability
   - Monitor FloodWait errors

2. **For Multiple Giveaways:**
   - Close finished giveaways regularly
   - Archive old data periodically
   - Monitor database size

3. **For Better Response Time:**
   - Run on VPS with good network
   - Use SSD storage
   - Keep Python dependencies updated

## Dependencies

- **aiogram** - Modern Telegram Bot API framework
- **pytz** - Timezone support
- **telethon** - MTProto Telegram client

## Contributing

1. Fork the repository
2. Create feature branch (`git checkout -b feature/improvement`)
3. Commit changes (`git commit -am 'Add new feature'`)
4. Push to branch (`git push origin feature/improvement`)
5. Create Pull Request

## Support

For issues, questions, or suggestions:

- **GitHub Issues:** https://github.com/fedyaqq34356/Random-bot/issues
- **Repository:** https://github.com/fedyaqq34356/Random-bot.git

## License

This project is open-source and free to use.

## Acknowledgments

- **aiogram** for the excellent Telegram Bot framework
- **Telethon** for MTProto implementation
- **Telegram** for the Bot API

---

Made with ❤️ for the Telegram community
