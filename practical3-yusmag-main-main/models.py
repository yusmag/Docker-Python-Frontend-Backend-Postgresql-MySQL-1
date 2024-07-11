from extensions import db
from sqlalchemy import text, exc

def create_user_tables():
    user_table_sql = text("""
        CREATE TABLE IF NOT EXISTS users (
            id INT AUTO_INCREMENT PRIMARY KEY,
            username VARCHAR(80) UNIQUE NOT NULL,
            password VARCHAR(64) NOT NULL, 
            email VARCHAR(120) UNIQUE NOT NULL,
            status ENUM('0','1','2') DEFAULT '0',
            modified_at TIMESTAMP DEFAULT CURRENT_TIMESTAMP,
            created_at TIMESTAMP DEFAULT CURRENT_TIMESTAMP
        )ENGINE=InnoDB;
    """)

    user_profile_table_sql = text("""
        CREATE TABLE IF NOT EXISTS user_profiles (
            id INT AUTO_INCREMENT PRIMARY KEY,
            user_id INT NOT NULL,
            first_name VARCHAR(100) NULL,
            last_name VARCHAR(100) NULL,
            contact_no VARCHAR(15),
            dob DATE NULL,
            bio TEXT,
            country VARCHAR(100) NULL,
            FOREIGN KEY (user_id) REFERENCES users(id)
        )ENGINE=InnoDB; 
    """)

    image_table_sql = text("""
        CREATE TABLE IF NOT EXISTS images (
            id INT AUTO_INCREMENT PRIMARY KEY,
            image_name VARCHAR(100) NOT NULL,
            image_url VARCHAR(255) NOT NULL,
            created_at TIMESTAMP DEFAULT CURRENT_TIMESTAMP
        )ENGINE=InnoDB; 
    """)

    user_image_table_sql = text("""
        CREATE TABLE IF NOT EXISTS user_image (
            user_id INT NOT NULL,
            image_id INT NOT NULL,
            PRIMARY KEY (user_id, image_id),
            FOREIGN KEY (user_id) REFERENCES users(id) ON DELETE CASCADE,
            FOREIGN KEY (image_id) REFERENCES images(id) ON DELETE CASCADE
        ) ENGINE=InnoDB;
    """)

    # role_table_sql = text("""
    #     CREATE TABLE IF NOT EXISTS roles (
    #         id INT AUTO_INCREMENT PRIMARY KEY,
    #         name CHAR(8) NOT NULL DEFAULT 'Standard',
    #         description VARCHAR(100) NULL
    #     )ENGINE=InnoDB;
    # """)

    with db.engine.begin() as connection:
        connection.execute(user_table_sql)
        connection.execute(user_profile_table_sql)
        connection.execute(image_table_sql)
        connection.execute(user_image_table_sql)
        # connection.execute(role_table_sql)

def initialize_database():
    """Create user tables if they don't exist before the first request."""
    create_user_tables()


### CRUD USER ###
#CREATE USER
def create_user(username, password, email):
    try:
        # Insert into users table
        user_sql = text("""
        INSERT INTO users (username, password, email) VALUES (:username, :password, :email);
        """)
        db.session.execute(user_sql, {'username': username, 'password': password, 'email': email})
        # Fetch the last inserted user_id
        user_id = db.session.execute(text('SELECT LAST_INSERT_ID();')).fetchone()[0] 
        db.session.commit()
        return user_id
    
    except Exception as e:
        # Rollback the transaction in case of error
        db.session.rollback()
        raise e   

#CREATE USER PROFILE
def create_user_profile(user_id, profile_data):
    
    try:
        # Insert into user_profiles table
        profile_sql = text("""
        INSERT INTO user_profiles (user_id, first_name, last_name, contact_no, dob, bio, country) VALUES (:user_id, :first_name, :last_name, :contact_no, :dob, :bio, :country)
        """)
        db.session.execute(profile_sql, {**profile_data, 'user_id': user_id})
        user_profile_id = db.session.execute(text('SELECT LAST_INSERT_ID();')).fetchone()[0]        
        db.session.commit()
        return user_profile_id
    except Exception as e:
        # Rollback the transaction in case of error
        db.session.rollback()
        raise e


def get_user_by_id(user_id):
    try:
        sql = text("SELECT id, username, email FROM users WHERE id = :user_id;")
        result = db.session.execute(sql, {'user_id': user_id})
        user = result.fetchone()

        # No need to commit() as no changes are being written to the database
        if user:
            # Convert the result into a dictionary if not None
            user_details = user._asdict()
            return user_details
        else:
            return None
    except Exception as e:
        # Rollback the transaction in case of error
        db.session.rollback()
        raise e


def get_user_details_by_id(user_id):
    try:
        sql = text("""
        SELECT 
            users.id as user_id, 
            users.username, 
            users.email, 
            user_profiles.first_name, 
            user_profiles.last_name, 
            user_profiles.contact_no, 
            user_profiles.dob, 
            user_profiles.bio, 
            user_profiles.country
        FROM 
            users
        LEFT JOIN 
            user_profiles ON users.id = user_profiles.user_id
        WHERE users.id = :user_id
        GROUP BY 
            users.id, 
            user_profiles.id;
        """)
        result = db.session.execute(sql, {'user_id': user_id})
        user_details = result.fetchone()
        return user_details._asdict() if user_details else None
    except Exception as e:
        # Rollback the transaction in case of error
        db.session.rollback()
        raise e

def create_user_image(user_id, image_name, image_url):
    try:
        print(image_name, image_url)
        # Insert into user_profiles table
        sql = text("""INSERT INTO images (image_name, image_url) VALUES (:image_name, :image_url)""")

        # execute query
        db.session.execute(sql, {'image_name': image_name, 'image_url' : image_url})

        # fetch the ID of the last inserted row
        image_id = db.session.execute(text('SELECT LAST_INSERT_ID();')).fetchone()[0]

        assign_image_sql = text("""
                                INSERT INTO user_image(user_id, image_id) VALUES (:user_id, :image_id);""")
        db.session.execute(assign_image_sql, {'user_id': user_id, 'image_id':image_id})
        db.session.commit()
        return image_id
    
    except Exception as e:
        # Rollback the transaction in case of error
        db.session.rollback()
        raise e

def get_user_profile_and_image_id(user_id):
    try:
        sql = text("""
        SELECT 
            users.id as user_id,
            users.username,
            users.email,
            users.status,
            user_profiles.first_name,
            user_profiles.last_name,
            user_profiles.contact_no,
            user_profiles.dob,
            user_profiles.bio,
            user_profiles.country,
            GROUP_CONCAT(images.image_name) as image_names,
            GROUP_CONCAT(images.image_url) as image_urls
        FROM 
            users
        LEFT JOIN
            user_profiles ON users.id = user_profiles.user_id
        LEFT JOIN
            user_image ON users.id = user_image.user_id
        LEFT JOIN
            images ON user_image.image_id = images.id
        WHERE users.id = :user_id
        GROUP BY
            users.id,
            user_profiles.id;
        """)
        result = db.session.execute(sql, {'user_id': user_id})
        user_details = result.fetchone()
        return user_details._asdict() if user_details else None
    except Exception as e:
        # Rollback the transaction in case of error
        db.session.rollback()
        raise e

def create_user_roles_id(user_id, name, description):
    try: 
        sql = text("""INSERT INTO roles (name, description) VALUES (:role_name, :role_description)""")
        result = db.session.execute(sql, {'role_name' : name, 'role_description' : description})
        db.session.commit()
        print(result.rowcount)
        if result.rowcount > 0:
            # Convert the result into a dictionary if not None
            # user_details = result._asdict()
            return {"user_id": user_id}
        else:
            return "Error"

    except Exception as e:
        # Rollback the transaction in case of error
        db.session.rollback()
        raise e
    
def update_user_roles_id(user_id, name, description):
    try: 
        sql = text("UPDATE roles SET name = :role_name, description = :role_description WHERE id = :user_id;")
        result = db.session.execute(sql, {'user_id' : user_id, 'role_name' : name, 'role_description' : description})
        db.session.commit()
        print(result.rowcount)
        if result.rowcount > 0:
            # Convert the result into a dictionary if not None
            # user_details = result._asdict()
            return {"user_id": user_id}
        else:
            return "Error"

    except Exception as e:
        # Rollback the transaction in case of error
        db.session.rollback()
        raise e

def get_user_role_id(user_id):
    try:
        sql = text("""
        SELECT 
            users.id as user_id, 
            users.username,
            roles.name,
            roles.description            
        FROM 
            users
        LEFT JOIN 
            roles ON users.id = roles.id
        WHERE users.id = :user_id
        GROUP BY 
            roles.id;
        """)
        result = db.session.execute(sql, {'user_id': user_id})
        user_details = result.fetchone()
        return user_details._asdict() if user_details else None
    except Exception as e:
        # Rollback the transaction in case of error
        db.session.rollback()
        raise e

def update_user_id(user_id, username, email):
    try:
        sql = text("UPDATE users SET username = :username, email = :email WHERE id = :user_id;")
        result = db.session.execute(sql, {'user_id': user_id, 'username' : username, 'email' : email})
        db.session.commit()
        print(result.rowcount)
        if result.rowcount > 0:
            # Convert the result into a dictionary if not None
            # user_details = result._asdict()
            return {"user_id": user_id}
        else:
            return None

    except Exception as e:
        # Rollback the transaction in case of error
        db.session.rollback()
        raise e

def update_user_profile(user_id, first_name, last_name, contact_no, dob, bio, country):
    try:
        sql = text("UPDATE user_profiles SET first_name = :first_name, last_name = :last_name, contact_no = :contact_no, dob = :dob, bio = :bio, country = :country WHERE user_id = :user_id;")
        result = db.session.execute(sql, {'user_id': user_id, 'first_name': first_name, 'last_name': last_name, 'contact_no': contact_no, 'dob': dob, 'bio': bio, 'country': country})
        db.session.commit()
        print(result.rowcount)
        if result.rowcount > 0:
            # Convert the result into a dictionary if not None
            # user_details = result._asdict()
            return {"user_id": user_id}
        else:
            return "Error"

    except Exception as e:
        # Rollback the transaction in case of error
        db.session.rollback()
        raise e

def create_user_with_details(username, password, email, profile_data, image_urls):
    pass

def get_users():
    sql = 'SELECT id, username, email FROM users;'
    result = db.session.execute(sql)
    users = [dict(row) for row in result]
    return users

def get_user_details():
    sql = text("""
    SELECT 
        users.id as user_id, 
        users.username, 
        users.email, 
        user_profiles.first_name, 
        user_profiles.last_name, 
        user_profiles.contact_no, 
        user_profiles.dob, 
        user_profiles.bio, 
        user_profiles.country, 
        GROUP_CONCAT(images.image_url) as image_urls
    FROM 
        users
    LEFT JOIN 
        user_profiles ON users.id = user_profiles.user_id
    LEFT JOIN 
        images ON users.id = images.user_id
    GROUP BY 
        users.id, 
        user_profiles.id;
    """)
    result = db.session.execute(sql)
    user_details = [row._asdict() for row in result]
    return user_details

def delete_user_by_id(user_id):
    try:
        sql = text ("""
                    UPDATE users SET status = 2
                    WHERE users.id = :user_id;""")
        result = db.session.execute(sql,{'user_id': user_id})
        db.session.commit()
        if result.rowcount > 0:
            return {"user_id": user_id}
        else:
            return None
    
    except Exception as e:
        # Rollback the transaction in case of error
        db.session.rollback()
        raise e

def delete_user_profiles_by_id(user_id):
    try: 
        # Delete user details by id
        sql = text ("DELETE FROM user_profiles WHERE user_id = :user_id")
        db.session.execute(sql,{'user_id': user_id})
        db.session.commit()
        return user_id
    
    except Exception as e:
        # Rollback the transaction in case of error
        db.session.rollback()
        raise e



