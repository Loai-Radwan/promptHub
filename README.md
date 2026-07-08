# PromptHub

PromptHub is a modern web application for creating, organizing, and sharing AI prompts. It provides a clean and intuitive interface where users can manage their personal prompt library, explore prompts from the community, and discover prompts for different AI models.

Built with Django, PromptHub focuses on providing a practical solution for developers, students, content creators, and AI enthusiasts who want a centralized place to organize their AI workflows.

## Features

### Authentication

- User registration and login
- Secure authentication
- Profile editing
- Avatar upload
- User biography
- Password management

### Prompt Management

- Create prompts
- Edit your own prompts
- Delete prompts
- View prompt details
- Markdown support
- Copy prompts with one click
- View counter
- Copy counter

### Organization

- Categories
- Search prompts
- Browse prompts by category
- AI model selection



### Ratings

- Rate prompts
- Average rating calculation
- One rating per user

### Dashboard

Personal dashboard displaying:

- Total prompts
- Total views
- Total copies
- Average rating

### Responsive Design

Fully responsive interface optimized for desktop, tablet, and mobile devices.

### Security

- CSRF protection
- Authentication & authorization
- Server-side validation
- Permission checks
- Custom 403 and 404 pages

---

## Built With

### Backend

- Python
- Django

### Frontend

- HTML5
- CSS3
- JavaScript
- Bootstrap 5

### Database

- SQLite

### Libraries

- Pillow
- markdown2

---

## Project Structure

```text
promptHub/
│
├── promptHub/
│   ├── settings.py
│   ├── urls.py
│   └── wsgi.py
│
├── prompts/
│   ├── migrations/
│   ├── static/
│   ├── templates/
│   ├── forms.py
│   ├── models.py
│   ├── urls.py
│   └── views.py
│
├── media/
├── manage.py
├── requirements.txt
└── README.md
```

---

## Installation

Clone the repository:

```bash
git clone https://github.com/Loai-Radwan/promptHub.git
cd promptHub
```

Create a virtual environment:

```bash
python -m venv venv
```

Activate it:

**Windows**

```bash
venv\Scripts\activate
```

**Linux / macOS**

```bash
source venv/bin/activate
```

Install dependencies:

```bash
pip install -r requirements.txt
```

Apply migrations:

```bash
python manage.py migrate
```

Create a superuser (optional):

```bash
python manage.py createsuperuser
```

Run the development server:

```bash
python manage.py runserver
```

Open your browser at:

```
http://127.0.0.1:8000/
```

---

## Screenshots

> Add screenshots or a short demo GIF here.

---

## Roadmap

- Prompt collections
- Advanced search and filtering
- Rich Markdown editor
- API support
- Dark mode
- Bookmarking
- Prompt version history

---


## Author

**Loai Alshujaa**

- GitHub: https://github.com/Loai-Radwan
- LinkedIn: [https://www.linkedin.com/in/loai-alshujaa/](https://www.linkedin.com/in/loai-alshujaa/)