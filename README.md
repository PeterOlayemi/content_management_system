# ByteWrite (Content Management System)

A robust, scalable, and feature-rich Content Management System built with Django, designed to streamline content creation and user engagement. This CMS project offers an intuitive and responsive interface, ideal for managing blogs, articles, user roles, and social media interactions.

## 🚀 Features

### 1. User Roles and Permissions
- Custom roles: **Writer** and **Reader**, assigned during registration.
- Role-based views and permissions using custom mixins.
- Separate apps for managing different roles:
  - **Writer App**: For article creation, management, and analytics.
  - **Reader App**: For browsing, liking, and commenting on articles.
  - **Admin App**: Custom admin panel for advanced content and user management.

### 2. Custom User Registration and Profile Management
- Unified registration form with dynamic fields based on role selection.
- Profile editing with current user data pre-filled and a separate password change feature.
- Social media link formatting for easy redirection.

### 3. Article and Category Management
- Articles categorized using **Many-to-Many relationship** with `Category` model.
- **View tracking**: Each article tracks the number of views and can be sorted by popularity.
- Like and unlike functionality using a Many-to-Many field for user engagement.

### 4. Comment System
- Nested comments with the ability to update and reply to existing comments.
- Comment form reuse for updating comments, enhancing user interactivity.

### 5. Custom Admin Panel
- A customized admin panel to provide better control over content and user management.
- Unique styling and additional features for enhanced usability.

### 6. Enhanced User Experience
- Site-wide contact information display via the `base.html` template.
- Customized pagination for articles.
- Django messages integrated into views for better user feedback.

### 7. Security Features
- Role-based access control using a custom mixin to restrict access to specific views.
- Redirect unauthorized users to the login page with a `next` URL parameter.

### 8. SEO and Social Media Integration
- Optional fields for social media links during registration, automatically formatted for redirection.
- Meta tags and social sharing features integrated into article views.

## Technologies Used

- **Frontend:** HTML, CSS, Bootstrap, JavaScript
- **Backend:** Python Django
- **Database:** SQLite (can be easily configured for other databases)

## 🛠️ Installation and Setup

### Step 1: Clone the Repository
    git clone https://github.com/PeterOlayemi/content_management_system.git

### Step 2: Create a Virtual Environment
    python -m venv env
    source env/bin/activate  # On Windows use `env\Scripts\activate`

### Step 3: Install Dependencies
    pip install -r requirements.txt

### Step 4: Configure Environment Variables
    Create environment variables (.env) file containing these variables (all vars are set to an empty string for testing purpose only):
    SECRET_KEY = '{{your_django_project_secret_key}}'
    my_email = '{{your_email_address}}'
    appsPassword = '{{your_appspassword_for_email}}'

### Step 5: Run Migrations
    python manage.py makemigrations
    python manage.py migrate

### Step 6: Create a Superuser
    python manage.py createsuperuser

### Step 7: Run the Development Server
    python manage.py runserver

### Visit http://localhost:8000 in your browser to see the CMS in action. In the django admin panel, add groups - 'Reader', 'Writer', 'Admin' and add the superuser to the 'Admin' so you can access the custom admin panel.

## Project Structure

content_management_system/
├── account/
├── administrator/
├── blog_site/
├── main/
├── media/
├── reader/
├── static/
├── writer/
├── .gitignore
├── LICENSE
├── manage.py
├── README.md
└── requirements.txt


## Contributing

Contributions are welcome! Please follow these steps:

1. Fork the project.

2. Create your feature branch (git checkout -b feature/YourFeature).

3. Commit your changes (git commit -m 'Add some feature').

4. Push to the branch (git push origin feature/YourFeature).

5. Open a Pull Request.


## License

This project is licensed under the [MIT License](LICENSE) - see the [LICENSE](LICENSE) file for details.

## Contact

For questions or feedback, please reach out:

Email: olayemipeter177@gmail.com

LinkedIn: [Visit My Profile](https://linkedin.com/in/petercontent)

Portfolio: [Visit My Website](https://peterolayemi.github.io)
