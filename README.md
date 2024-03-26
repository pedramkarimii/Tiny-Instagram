# Tiny Instagram Django Models

This repository contains Django models representing users, profiles, posts, comments, and OTP (One Time Password) codes for Tiny Instagram.

## Models Overview

Tiny Instagram is a simplified version of the popular social media platform Instagram, implemented using Django models. This project provides the foundational database structure and models necessary to build a basic social media platform with user authentication, profile management, post sharing, commenting, and OTP-based account verification.

### User
Represents a user in the application. It stores basic user information such as username, email, and phone number, along with flags indicating user activity and privileges.

### Profile
Extends the User model and represents additional information associated with a user, including full name, gender, age, biography, and profile picture. It also manages relationships such as followers and following.

### Post
Represents a post in the application. It contains fields for the post content, including text and images, along with metadata such as creation time and owner.

### Comment
Represents a comment on a post. Users can comment on posts, and comments can be replies to other comments. Comments include the comment text and metadata such as creation time and owner.

### OptCode
Handles OTP (One Time Password) codes for account verification. It stores the OTP code, associated phone number or email, and creation time.

## Entity-Relationship Diagram (ERD)

The following is a textual representation of the Entity-Relationship Diagram (ERD) illustrating the relationships between the models in Tiny Instagram:

```
╔════════════════════════════════════════════════════════════════╗
║                          User Model                            ║
╠═════════════════════════════╦══════════════════════════════════╣
║         Attribute           ║           Description            ║
╠═════════════════════════════╬══════════════════════════════════╣
║ username: CharField         ║ Username of the user.            ║
║ email: EmailField           ║ Email address of the user.       ║
║ phone_number: CharField     ║ Phone number of the user.        ║
║ create_time: DateTimeField  ║ Time when the user was created.  ║
║ update_time: DateTimeField  ║ Time when the user was last      ║
║                             ║ updated.                         ║
║ is_deleted: BooleanField    ║ Indicates if the user is deleted.║
║ is_active: BooleanField     ║ Indicates if the user is active. ║
║ is_admin: BooleanField      ║ Indicates if the user is an      ║
║                             ║ admin.                           ║
║ is_staff: BooleanField      ║ Indicates if the user is staff.  ║
║ is_superuser: BooleanField  ║ Indicates if the user is a       ║
║                             ║ superuser.                       ║
╚════════════════════════════════════════════════════════════════╝

╔════════════════════════════════════════════════════╗
║                    Profile Table                   ║
╠════════════════════════════════════════════════════╣
║ id, user_id (FK), full_name, name, last_name,      ║
║ gender, age, bio, profile_picture, is_deleted,     ║
║ is_active, create_time (auto_now_add=True,         ║
║ editable=False), update_time (auto_now=True,       ║
║ editable=False)                                    ║
╚════════════════════════════════════════════════════╝
╔══════════════════════════════════════════════════════╗
║                     Post Table                       ║
╠══════════════════════════════════════════════════════╣
║ id, owner_id (FK), title, body, post_picture,        ║
║ is_deleted (default=False), is_active (default=True),║
║ delete_time (auto_now=True, editable=False),         ║
║ create_time (auto_now_add=True, editable=False),     ║
║ update_time (auto_now=True, editable=False)          ║
╚══════════════════════════════════════════════════════╝

╔════════════════════════════════════════════════════╗
║                    Comment Table                   ║
╠════════════════════════════════════════════════════╣
║ id, owner_id (FK), post_id (FK), reply_id (FK),    ║
║ is_reply, comments, is_deleted (default=False),    ║
║ delete_time (auto_now=True, editable=False),       ║
║ create_time (auto_now_add=True, editable=False),   ║
║ update_time (auto_now=True, editable=False)        ║
╚════════════════════════════════════════════════════╝

╔════════════════════════════════════════════════════╗
║                     Vote Table                     ║
╠════════════════════════════════════════════════════╣
║ id, user_id (FK), post_id (FK),                    ║
║ create_time (auto_now_add=True, editable=False)    ║
╚════════════════════════════════════════════════════╝
╔═══════════════════════════════════════════════════════════════════════╗
║                             OptCode Model                             ║
╠═══════════════════════════════════════════════════════════════════════╣
║ code: PositiveSmallIntegerField                                       ║
║ phone_number: CharField (max_length=11, unique=True)                  ║
║ email: EmailField (max_length=100, unique=True, null=True, blank=True)║
║ created: DateTimeField (auto_now_add=True)                            ║
║ is_used: BooleanField (default=False)                                 ║
╠═══════════════════════════════════════════════════════════════════════╝

```


## Project Overview

Tiny Instagram aims to offer a lightweight and modular solution for developers looking to kickstart their own social media projects. By providing a set of Django models, Tiny Instagram allows developers to focus on implementing business logic, user interfaces, and additional features specific to their application.

## How to Use the Project

1. **Clone the Repository**: Clone the Tiny Instagram repository to your local machine using Git.
    ```
    git clone https://github.com/pedramkarimii/social-media.git
    ```
2. **Install Dependencies**: Install the required Python dependencies listed in the `requirements.txt` file.
    ```
    pip install -r requirements.txt
    ```
3. **Set Up Django Environment**: Navigate to the project directory and set up the Django environment by running migrations and creating a superuser.
    ```
    cd social-media
    python manage.py migrate
    python manage.py createsuperuser
    ```
4. **Start the Development Server**: Start the Django development server to run the Tiny Instagram application locally.
    ```
    python manage.py runserver
    ```
5. **Access the Application**: Access the Tiny Instagram application through your web browser at the specified URL (typically `http://127.0.0.1:8000/`) to interact with the implemented models.

## How to Fork the Project

To fork the Tiny Instagram project and contribute to it:

1. **Fork the Repository**: Click the "Fork" button at the top right of the GitHub repository page to create a copy of the project in your GitHub account.
2. **Clone Your Forked Repository**: Clone your forked repository to your local machine using Git.
3. **Make Changes and Improvements**: Make changes and improvements to the project as needed, such as adding new features, fixing bugs, or enhancing documentation.
4. **Commit and Push Changes**: Commit your changes to your forked repository and push them to GitHub.
5. **Create a Pull Request**: Create a pull request to propose your changes and merge them into the main repository.

## Contributors

- Pedram Karimi (@pedramkarimii) - Owner

