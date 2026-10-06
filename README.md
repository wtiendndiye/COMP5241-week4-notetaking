# NoteTaker - Personal Note Management Application

A modern, responsive web application for managing personal notes with a beautiful user interface and full CRUD functionality.

## 🌟 Features

- **Create Notes**: Add new notes with titles and rich content
- **Edit Notes**: Update existing notes with real-time editing
- **Delete Notes**: Remove notes you no longer need
- **Search Notes**: Find notes quickly by searching titles and content
- **Auto-save**: Notes are automatically saved as you type
- **Responsive Design**: Works perfectly on desktop and mobile devices
- **Modern UI**: Beautiful gradient design with smooth animations
- **Real-time Updates**: Instant feedback and updates

## 🚀 Live Demo

The application is deployed and accessible at: **https://3dhkilc88dkk.manus.space**

## 🛠 Technology Stack

### Frontend
- **HTML5**: Semantic markup structure
- **CSS3**: Modern styling with gradients, animations, and responsive design
- **JavaScript (ES6+)**: Interactive functionality and API communication

### Backend
- **Python Flask**: Web framework for API endpoints
- **SQLAlchemy**: ORM for database operations
- **Flask-CORS**: Cross-origin resource sharing support

### Database
- **SQLite**: Local development database
- **Neon PostgreSQL**: External persistent database for Vercel deployment

## 📁 Project Structure

```
notetaking-app/
├── src/
│   ├── models/
│   │   ├── user.py          # User model (template)
│   │   └── note.py          # Note model with database schema
│   ├── routes/
│   │   ├── user.py          # User API routes (template)
│   │   └── note.py          # Note API endpoints
│   └── main.py              # Flask application entry point
├── public/
│   ├── index.html           # Frontend application (served by Vercel CDN)
│   └── favicon.ico          # Application icon
├── database/
│   └── app.db               # Local SQLite database (ignored by Git)
├── venv/                    # Python virtual environment
├── requirements.txt         # Python dependencies
├── vercel.json              # Vercel function configuration
└── README.md               # This file
```

## 🔧 Local Development Setup

### Prerequisites
- Python 3.11+
- pip (Python package manager)

### Installation Steps

1. **Clone or download the project**
   ```bash
   python -m venv venv
   ```

2. **Activate the virtual environment**
   ```bash
   source venv/bin/activate
   ```

   Remark: On Windows, use `venv\Scripts\activate`

3. **Install dependencies**
   ```bash
   pip install -r requirements.txt
   ```

4. **Run the application**
   ```bash
   python src/main.py
   ```

5. **Access the application**
   - Open your browser and go to `http://localhost:5001`

### Translation setup

The title, content, and whole-note translation buttons use DeepSeek through
OpenRouter. For local development, create an OpenRouter API key and put it in
the root `.env` file:

```dotenv
OPENROUTER_API_KEY=your-openrouter-api-key
```

The repository ignores `.env`, so the key will not be committed. `.env.example`
shows the expected format. The app loads `.env` when it starts; restart it after
editing the file. Translation uses `nvidia/nemotron-3.5-lightning:free` with
reasoning enabled by default. To select another model available to your
OpenRouter account, set `OPENROUTER_MODEL` in `.env`. Translation detects
English or Simplified Chinese and translates to the other language. The API key
stays on the server and is never sent to the browser. Free model availability
and rate limits are controlled by OpenRouter.

### Deploying to Vercel

The app uses SQLite locally and Neon PostgreSQL in deployment. Create a Neon
project in the Neon Console, then copy its connection string from the
**Connect** dialog. Use the pooled connection string for Vercel serverless
deployments and ensure SSL is enabled. Never commit database credentials or
import `.env` into Vercel.

1. Push the project to GitHub and import the repository in Vercel.
2. Set the **Framework Preset** to **Flask** (or let Vercel detect Flask).
   Keep the **Root Directory** at the repository root. Leave **Build Command**,
   **Output Directory**, and **Install Command** at their defaults/overrides
   disabled; Vercel detects `src/main.py` and installs `requirements.txt`.
3. In **Settings → Environment Variables**, add these variables for Production
   (and Preview if needed):
   - `DATABASE_URL` — Neon PostgreSQL connection string copied from the
     project's **Connect** dialog. Select the pooled connection option for
     Vercel.
   - `OPENROUTER_API_KEY` — your OpenRouter API key.
   - `OPENROUTER_MODEL` — optional; defaults to
     `nvidia/nemotron-3.5-lightning:free`.
4. Save the settings and deploy/redeploy. Vercel serves `public/` as static
   assets and runs the Flask application as a Python Function. Verify the
   deployment by opening its URL and creating a note. The database tables are
   created automatically when the function starts.

Vercel's filesystem is not persistent, so `DATABASE_URL` is required there;
the app deliberately fails at startup instead of silently using ephemeral
SQLite. Configure the variables in Vercel itself—do not upload the local
`.env` file.

For local testing with Neon, put its connection string in the ignored root
`.env` as `DATABASE_URL=...`, then restart the app. When `DATABASE_URL` is set,
the app connects to Neon instead of the local SQLite database. Verify
persistence by creating a note, restarting the app, and confirming the note
still appears. Do not share or commit the connection string.

## 📡 API Endpoints

### Notes API
- `GET /api/notes` - Get all notes
- `POST /api/notes` - Create a new note
- `GET /api/notes/<id>` - Get a specific note
- `PUT /api/notes/<id>` - Update a note
- `DELETE /api/notes/<id>` - Delete a note
- `GET /api/notes/search?q=<query>` - Search notes

### Translation API
- `POST /api/translate` - Translate a title, content, or both. The JSON body
  includes `field` (`title`, `content`, or `all`) and the corresponding text
  field(s). It returns the translated field(s).

### Request/Response Format
```json
{
  "id": 1,
  "title": "My Note Title",
  "content": "Note content here...",
  "created_at": "2025-09-03T11:26:38.123456",
  "updated_at": "2025-09-03T11:27:30.654321"
}
```

## 🎨 User Interface Features

### Sidebar
- **Search Box**: Real-time search through note titles and content
- **New Note Button**: Create new notes instantly
- **Notes List**: Scrollable list of all notes with previews
- **Note Previews**: Show title, content preview, and last modified date

### Editor Panel
- **Title Input**: Edit note titles
- **Content Textarea**: Rich text editing area
- **Save Button**: Manual save option (auto-save also available)
- **Delete Button**: Remove notes with confirmation
- **Real-time Updates**: Changes reflected immediately

### Design Elements
- **Gradient Background**: Beautiful purple gradient backdrop
- **Glass Morphism**: Semi-transparent panels with backdrop blur
- **Smooth Animations**: Hover effects and transitions
- **Responsive Layout**: Adapts to different screen sizes
- **Modern Typography**: Clean, readable font stack

## 🔒 Database Schema

### Notes Table
```sql
CREATE TABLE note (
    id INTEGER PRIMARY KEY,
    title VARCHAR(200) NOT NULL,
    content TEXT NOT NULL,
    created_at DATETIME DEFAULT CURRENT_TIMESTAMP,
    updated_at DATETIME DEFAULT CURRENT_TIMESTAMP
);
```

## 🚀 Deployment

The application is configured for easy deployment with:
- CORS enabled for cross-origin requests
- Host binding to `0.0.0.0` for external access
- Production-ready Flask configuration
- Neon PostgreSQL configured through `DATABASE_URL`

## 🔧 Configuration

### Environment Variables
- `FLASK_ENV`: Set to `development` for debug mode
- `SECRET_KEY`: Flask secret key for sessions

### Database Configuration
- Database file: `src/database/app.db`
- Automatic table creation on first run
- SQLAlchemy ORM for database operations

## 📱 Browser Compatibility

- Chrome/Chromium (recommended)
- Firefox
- Safari
- Edge
- Mobile browsers (iOS Safari, Chrome Mobile)

## 🤝 Contributing

1. Fork the repository
2. Create a feature branch
3. Make your changes
4. Test thoroughly
5. Submit a pull request

## 📄 License

This project is open source and available under the MIT License.

## 🆘 Support

For issues or questions:
1. Check the browser console for error messages
2. Verify the Flask server is running
3. Ensure all dependencies are installed
4. Check network connectivity for the deployed version

## 🎯 Future Enhancements

Potential improvements for future versions:
- User authentication and multi-user support
- Note categories and tags
- Rich text formatting (bold, italic, lists)
- File attachments
- Export functionality (PDF, Markdown)
- Dark/light theme toggle
- Offline support with service workers
- Note sharing capabilities

---

**Built with ❤️ using Flask, SQLAlchemy, and modern web technologies**
