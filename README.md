# Tiny Instagram Platform Features

1. **User Authentication and Profiles**:
    - User registration and login.
    - User profile management: editing personal information, uploading profile pictures, etc.
    - User roles and permissions (e.g., admin, regular user).
    - Delete account: users can delete their accounts permanently.

2. **Social Interaction**:
    - Friendship/following system: users can follow/unfollow other users.
    - Like posts: users can like posts shared by other users.
    - Like comments: users can like comments made on posts.
    - Like comment replies: users can like replies to comments.
    - Commenting: users can comment on posts.
    - Reply to comments: users can reply to comments made on posts.
    - Delete post: users can delete posts they have created.
    - Delete comment: users can delete comments they have made.

3. **Content Creation and Sharing**:
    - Creating posts: users can create and share text, images, videos, or links.
    - Commenting: users can comment on posts and reply to comments.

4. **Content Discovery and Exploration**:
    - Explore or discover page: users can discover new content, trending topics, or popular users.
5. **Privacy and Security**:
    - Privacy settings: users can control who can see their posts and profile information.
    - Reporting and blocking: users can report inappropriate content or block other users.
    - Change password: users can change their account password.
6. **Post and Account Updates**:
    - Update post: users can edit and update posts they have created.
    - Update account: users can edit and update their account information.
    - Update profile: users can update their profile information, such as bio, profile picture, etc.

## Technologies Used

- **Backend**:
    - Django: A high-level Python web framework that encourages rapid development and clean, pragmatic design. Used for
      building the backend of the social media platform, handling user authentication, data modeling, URL routing, and
      more.
    - PostgreSQL: A powerful open-source relational database management system used for storing data related to users,
      posts, comments, etc.
    - Redis: An in-memory data structure store, used as a caching layer to improve performance and scalability.

- **Frontend**:
    - HTML: The standard markup language for creating web pages.
    - Tailwind CSS: A utility-first CSS framework used for styling the user interface, providing a highly customizable
      and responsive design.
    - AJAX (Asynchronous JavaScript and XML): A set of web development techniques used to create asynchronous web
      applications, enabling data to be exchanged with the server asynchronously without interfering with the display
      and behavior of the existing page.


- **Version Control**:
    - Git: A distributed version control system used for tracking changes in source code during development,
      facilitating collaboration among team members and managing project history.

- **Development Environment**:
    - Virtual Environment (venv): A tool to create isolated Python environments, ensuring project dependencies are
      managed separately from other projects and system-wide installations.

# Entity-Relationship Diagram (ERD)

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
║                   Relation Table                   ║
╠════════════════════════════════════════════════════╣
║ id (PK)                                            ║
║ followers_id (FK)                                  ║
║ following_id (FK)                                  ║
║ is_follow                                          ║
║ create_time (auto_now_add=True, editable=False)    ║
╚════════════════════════════════════════════════════╝

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
║                    Image Table                     ║
╠════════════════════════════════════════════════════╣
║ id (PK)                                            ║
║ post_id (FK)                                       ║
║ images                                             ║
║ is_deleted (default=False)                         ║
║ is_active (default=True)                           ║
║ delete_time (auto_now=True, editable=False)        ║
║ create_time (auto_now_add=True, editable=False)    ║
║ update_time (auto_now=True, editable=False)        ║
╚════════════════════════════════════════════════════╝


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
║                  CommentLike Table                 ║
╠════════════════════════════════════════════════════╣
║ id (PK)                                            ║
║ user_id (FK)                                       ║
║ comment_id (FK)                                    ║
║ create_time (auto_now_add=True, editable=False)    ║
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
╚═══════════════════════════════════════════════════════════════════════╝

```

## Entities:

1. **User Model**:
    - Attributes:
        - username: CharField
        - email: EmailField
        - phone_number: CharField
        - create_time: DateTimeField
        - update_time: DateTimeField
        - is_deleted: BooleanField
        - is_active: BooleanField
        - is_admin: BooleanField
        - is_staff: BooleanField
        - is_superuser: BooleanField

2. **Relation Table**:
    - Attributes:
        - id: Primary Key
        - followers_id: Foreign Key
        - following_id: Foreign Key
        - is_follow: Boolean

3. **Profile Table**:
    - Attributes:
        - id: Primary Key
        - user_id: Foreign Key
        - full_name: CharField
        - name: CharField
        - last_name: CharField
        - gender: CharField
        - age: IntegerField
        - bio: TextField
        - profile_picture: ImageField
        - is_deleted: BooleanField
        - is_active: BooleanField
        - create_time: DateTimeField
        - update_time: DateTimeField

4. **Post Table**:
    - Attributes:
        - id: Primary Key
        - owner_id: Foreign Key
        - title: CharField
        - body: TextField
        - post_picture: ImageField
        - is_deleted: BooleanField
        - is_active: BooleanField
        - delete_time: DateTimeField
        - create_time: DateTimeField
        - update_time: DateTimeField

5. **Image Table**:
    - Attributes:
        - id: Primary Key
        - post_id: Foreign Key
        - images: ImageField
        - is_deleted: BooleanField
        - is_active: BooleanField
        - delete_time: DateTimeField
        - create_time: DateTimeField
        - update_time: DateTimeField

6. **Comment Table**:
    - Attributes:
        - id: Primary Key
        - owner_id: Foreign Key
        - post_id: Foreign Key
        - reply_id: Foreign Key
        - is_reply: BooleanField
        - comments: TextField
        - is_deleted: BooleanField
        - delete_time: DateTimeField
        - create_time: DateTimeField
        - update_time: DateTimeField

7. **CommentLike Table**:
    - Attributes:
        - id: Primary Key
        - user_id: Foreign Key
        - comment_id: Foreign Key
        - create_time: DateTimeField

8. **Vote Table**:
    - Attributes:
        - id: Primary Key
        - user_id: Foreign Key
        - post_id: Foreign Key
        - create_time: DateTimeField

9. **OptCode Model**:
    - Attributes:
        - code: PositiveSmallIntegerField
        - phone_number: CharField (max_length=11, unique=True)
        - email: EmailField (max_length=100, unique=True, null=True, blank=True)
        - created: DateTimeField (auto_now_add=True)
        - is_used: BooleanField (default=False)

## Project Overview

Tiny Instagram aims to offer a lightweight and modular solution for developers looking to kickstart their own social
media projects. By providing a set of Django models, Tiny Instagram allows developers to focus on implementing business
logic, user interfaces, and additional features specific to their application.

## How to Use the Project

1. **Clone the Repository**: Clone the Tiny Instagram repository to your local machine using Git.
    ```
    git clone https://github.com/pedramkarimii/social-media.git
    ```
2. **Install Dependencies**: Install the required Python dependencies listed in the `requirements.txt` file.
    ```
    pip install -r requirements.txt
    ```
3. **Set Up Django Environment**: Navigate to the project directory and set up the Django environment by running
   migrations and creating a superuser.
    ```
    cd social-media
    python manage.py migrate
    python manage.py createsuperuser
    ```
4. **Start the Development Server**: Start the Django development server to run the Tiny Instagram application locally.
    ```
    python manage.py runserver
    ```
5. **Access the Application**: Access the Tiny Instagram application through your web browser at the specified URL (
   typically `http://127.0.0.1:8000/`) to interact with the implemented models.

## How to Fork the Project

To fork the Tiny Instagram project and contribute to it:

1. **Fork the Repository**: Click the "Fork" button at the top right of the GitHub repository page to create a copy of
   the project in your GitHub account.
2. **Clone Your Forked Repository**: Clone your forked repository to your local machine using Git.
3. **Make Changes and Improvements**: Make changes and improvements to the project as needed, such as adding new
   features, fixing bugs, or enhancing documentation.
4. **Commit and Push Changes**: Commit your changes to your forked repository and push them to GitHub.
5. **Create a Pull Request**: Create a pull request to propose your changes and merge them into the main repository.

## Contributors

- Pedram Karimi (@pedramkarimii) - Owner

