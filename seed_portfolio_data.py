import sqlite3
import os
from datetime import datetime
from werkzeug.security import generate_password_hash

# Ensure instance directory exists
os.makedirs('instance', exist_ok=True)

# Connect to database
conn = sqlite3.connect('instance/portfolio.db')
conn.row_factory = sqlite3.Row
db = conn

print("Seeding portfolio data to the new table structure...")

# About data
about_content = """
<p>I'm <strong>Ashish Pal</strong>, a third-year B.Tech student in Computer Science Engineering with expertise in Python, Java, Flask, and Android development.</p>

<p>I have built projects like MyManager (Java-based Android app with Firebase), Breezy (Gemini API), and Notes API. As the Technical Head at Ekume Club, I've developed strong leadership and collaboration skills, backed by internships at CodeClause, Cognifyz, and Bharat Intern.</p>

<p>My technical skills include Python, Java, JavaScript, HTML, CSS, Flask, Bootstrap, Android development, Docker, AWS, Render, SQLite3, RESTful APIs, Gmail API, Gemini API, JWT, Socket.io, and Firebase.</p>

<p>I'm passionate about creating practical software solutions and sharing knowledge through workshops and events.</p>

<h4>Contact Information</h4>
<ul>
    <li>Email: palbro86@gmail.com</li>
    <li>Phone: 7428450179</li>
    <li>LinkedIn: <a href="https://www.linkedin.com/in/ashish-pal-5725a6257/" target="_blank">linkedin.com/in/ashish-pal-5725a6257</a></li>
    <li>GitHub: <a href="https://github.com/ashupal86/" target="_blank">github.com/ashupal86</a></li>
</ul>
"""

# Insert About content (append, don't delete)
about_count = db.execute('SELECT COUNT(*) as count FROM About').fetchone()['count']
if about_count == 0:
    print("Adding About content...")
    db.execute('INSERT INTO About (content) VALUES (?)', (about_content,))
else:
    print(f"Skipping About content (already have {about_count} entries)")

# Insert Skills
skills_data = [
    # Technical Skills
    ('Python', 'Programming Languages', 90, 'fab fa-python', 1),
    ('Java', 'Programming Languages', 85, 'fab fa-java', 2),
    ('JavaScript', 'Programming Languages', 80, 'fab fa-js', 3),
    ('HTML', 'Web Development', 95, 'fab fa-html5', 4),
    ('CSS', 'Web Development', 90, 'fab fa-css3-alt', 5),
    ('Flask', 'Frameworks', 90, 'fas fa-flask', 6),
    ('Bootstrap', 'Frameworks', 85, 'fab fa-bootstrap', 7),
    ('Android', 'Mobile Development', 80, 'fab fa-android', 8),
    ('Docker', 'DevOps', 75, 'fab fa-docker', 9),
    ('AWS', 'Cloud Services', 70, 'fab fa-aws', 10),
    ('Render', 'Cloud Services', 70, 'fas fa-cloud', 11),
    ('SQLite3', 'Databases', 85, 'fas fa-database', 12),
    ('RESTful APIs', 'Backend Development', 85, 'fas fa-code', 13),
    ('Gmail API', 'APIs', 80, 'fas fa-envelope', 14),
    ('Gemini API', 'APIs', 80, 'fas fa-robot', 15),
    ('JWT', 'Security', 75, 'fas fa-key', 16),
    ('Socket.io', 'Web Development', 70, 'fas fa-plug', 17),
    ('Firebase', 'Databases', 80, 'fas fa-fire', 18),
    
    # Soft Skills
    ('Team Leadership', 'Soft Skills', 90, 'fas fa-users', 19),
    ('Communication', 'Soft Skills', 85, 'fas fa-comments', 20),
    ('Problem-Solving', 'Soft Skills', 90, 'fas fa-puzzle-piece', 21),
    ('Time Management', 'Soft Skills', 85, 'fas fa-clock', 22),
    ('Collaboration', 'Soft Skills', 90, 'fas fa-handshake', 23),
]

# Check if skills already exist
skills_count = db.execute('SELECT COUNT(*) as count FROM Skill').fetchone()['count']
if skills_count == 0:
    print("Adding skills data...")
    for skill in skills_data:
        db.execute('''
        INSERT INTO Skill (name, category, proficiency, icon, display_order)
        VALUES (?, ?, ?, ?, ?)
        ''', skill)
else:
    print(f"Skipping skills data (already have {skills_count} entries)")

# Insert Education
education_data = [
    ('Noida Institute of Engineering & Technology', 'B.Tech', 'Computer Science Engineering', 
     '2022-06-01', '2026-05-31', 'CGPA: 6.5/9.9 (up to 5th semester)')
]

# Check if education entries already exist
education_count = db.execute('SELECT COUNT(*) as count FROM Education').fetchone()['count']
if education_count == 0:
    print("Adding education data...")
    for edu in education_data:
        db.execute('''
        INSERT INTO Education (institution, degree, field, start_date, end_date, description)
        VALUES (?, ?, ?, ?, ?, ?)
        ''', edu)
else:
    print(f"Skipping education data (already have {education_count} entries)")

# Insert Projects
projects_data = [
    ('MyManager', 'In Development', 
     'Java-based Android app with Firebase for merchant-distributor management.',
     'img/projects/mymanager.jpg', 'https://github.com/ashupal86/MyManager', 
     'https://github.com/ashupal86/MyManager', 'Java, Android, Firebase', 1, 'Mobile App'),
    
    ('Breezy', 'In Development',
     'Gamified platform with AI chat using Gemini API.',
     'img/projects/breezy.jpg', '', 'https://github.com/ashupal86', 
     'Python, Flask, Gemini API, SQLite3, HTML, CSS, JavaScript', 1, 'Web App'),
    
    ('Notes API', 'Completed',
     'RESTful API for note management with authentication.',
     'img/projects/notes-api.jpg', 'https://github.com/ashupal86/Notes-api', 
     'https://github.com/ashupal86/Notes-api', 'Python, Flask, SQLite3, JWT', 0, 'API'),
    
    ('Blog Website', 'Completed',
     'Personal blog with categories and comments.',
     'img/projects/blog.jpg', 'https://github.com/ashupal86/Blog-Website', 
     'https://github.com/ashupal86/Blog-Website', 'Flask, SQLite3, HTML, CSS, JavaScript, Bootstrap', 0, 'Web App'),
    
    ('ZOrder', 'In Development',
     'Real-time order management Android app.',
     'img/projects/zorder.jpg', '', 'https://github.com/ashupal86', 
     'Java, Android, Firebase', 0, 'Mobile App'),
    
    ('Interno - Edukul Education Center', 'Completed',
     'Responsive educational website.',
     'img/projects/interno.jpg', '', 'https://github.com/ashupal86', 
     'HTML, CSS, JavaScript, Bootstrap', 0, 'Web App'),
    
    ('Project Management Web App', 'In Development',
     'Web application for project management.',
     'img/projects/project-management.jpg', 'https://github.com/ashupal86/project-management-web-app', 
     'https://github.com/ashupal86/project-management-web-app', 'HTML, CSS, JavaScript, Flask', 0, 'Web App'),
    
    ('Portfolio', 'Completed',
     'Personal portfolio website.',
     'img/projects/portfolio.jpg', 'https://github.com/ashupal86/portfolio', 
     'https://github.com/ashupal86/portfolio', 'HTML, CSS, JavaScript, Flask', 1, 'Web App'),
]

# Check if projects already exist
projects_count = db.execute('SELECT COUNT(*) as count FROM Project').fetchone()['count']
if projects_count == 0:
    print("Adding projects data...")
    for project in projects_data:
        db.execute('''
        INSERT INTO Project (title, category, description, image, live_link, github_link, categories, featured, category)
        VALUES (?, ?, ?, ?, ?, ?, ?, ?, ?)
        ''', project)
else:
    print(f"Skipping projects data (already have {projects_count} entries)")

# Insert Achievements
achievements_data = [
    ('1st Place, Web Showdown (ISTE NIET)', 
     'Won first place in the Web Showdown competition organized by ISTE NIET, demonstrating exceptional web development skills.',
     '2023-11-15', 'img/achievements/web-showdown.jpg'),
    
    ('3rd Place, Webathon',
     'Secured third position in Webathon, showcasing creativity and technical prowess in web development under time constraints.',
     '2023-09-20', 'img/achievements/webathon.jpg'),
    
    ('Certificate of Appreciation, Deployment Workshop Host',
     'Received recognition for hosting a successful workshop on deployment practices using Docker, AWS, and Render.',
     '2024-02-10', 'img/achievements/deployment-workshop.jpg'),
    
    ('Certificate of Appreciation, AR Odyssey Event',
     'Acknowledged for organizing the AR Odyssey event, promoting augmented reality technologies among peers.',
     '2023-12-05', 'img/achievements/ar-odyssey.jpg'),
    
    ('Certificate of Recognition, BharatXR',
     'Recognized by BharatXR for contributions to the extended reality community and participation in their programs.',
     '2024-01-15', 'img/achievements/bharatxr.jpg'),
]

# Check if achievements already exist
achievements_count = db.execute('SELECT COUNT(*) as count FROM Achievement').fetchone()['count']
if achievements_count == 0:
    print("Adding achievements data...")
    for achievement in achievements_data:
        db.execute('''
        INSERT INTO Achievement (title, description, date, image)
        VALUES (?, ?, ?, ?)
        ''', achievement)
else:
    print(f"Skipping achievements data (already have {achievements_count} entries)")

# Sample blog posts
blog_post = (
    'My Journey as a Technical Head at Ekume Club',
    'my-journey-as-technical-head-ekume-club',
    """
    <p>As the Technical Head of Ekume Club at NIET, I've had the opportunity to lead various projects and initiatives that have contributed significantly to my professional growth. In this post, I'd like to share some of my experiences and learnings from this role.</p>
    
    <h3>Project Leadership</h3>
    <p>One of my primary responsibilities has been to lead Python, Java, and Android projects within the club. This has involved not only developing software but also mentoring other club members, coordinating team efforts, and ensuring project deliverables are met on time.</p>
    
    <h3>Workshop Hosting</h3>
    <p>I've organized and hosted several workshops on Docker, AWS, and Render for more than 50 peers. These workshops aimed to bridge the gap between theoretical knowledge and practical application, providing students with hands-on experience with industry-standard tools.</p>
    
    <h4>Key Learnings:</h4>
    <ul>
        <li>Effective communication is crucial when explaining complex technical concepts to audiences with varying levels of expertise.</li>
        <li>Practical demonstrations are more impactful than theoretical explanations.</li>
        <li>Preparation and thorough testing of all examples before a workshop is essential for smooth delivery.</li>
    </ul>
    
    <h3>Building a Technical Community</h3>
    <p>Beyond project work and workshops, I've been focused on building a vibrant technical community within our college. This has involved organizing coding competitions, hackathons, and tech talks.</p>
    
    <p>The experience has taught me valuable lessons about leadership, technical communication, and project management that complement my technical skills and will serve me well in my future career.</p>
    
    <h3>Future Directions</h3>
    <p>Looking ahead, I'm excited to introduce more advanced workshops on emerging technologies like AI and machine learning, expand our project portfolio, and create more opportunities for students to gain practical experience.</p>
    """,
    'img/blog/technical-head.jpg',
)

blog_post2 = (
    'My Experience with the Gemini API',
    'my-experience-with-gemini-api',
    """
    <p>The Google Gemini API has been a game-changer for my recent project, Breezy. In this post, I'll share my experience working with this powerful AI tool and how it enhanced my application.</p>
    
    <h3>What is Gemini API?</h3>
    <p>Gemini is Google's most capable AI model, designed to be multimodal from the ground up. It can understand and combine different types of information including text, code, audio, image, and video.</p>
    
    <h3>Implementing Gemini in Breezy</h3>
    <p>For my project Breezy, I wanted to create a gamified platform with AI chat capabilities. The Gemini API was the perfect solution, offering:</p>
    <ul>
        <li>Natural conversation flows with users</li>
        <li>Ability to understand context and maintain coherent dialogues</li>
        <li>Support for creative content generation</li>
        <li>Code understanding and assistance</li>
    </ul>
    
    <h3>Technical Implementation</h3>
    <p>Integration was relatively straightforward. After obtaining an API key, I used the Python client library:</p>
    
    <pre><code>
    import google.generativeai as genai
    
    genai.configure(api_key='YOUR_API_KEY')
    model = genai.GenerativeModel('gemini-pro')
    
    response = model.generate_content('Tell me about Flask development')
    print(response.text)
    </code></pre>
    
    <h3>Challenges Faced</h3>
    <p>Working with the API wasn't without challenges:</p>
    <ul>
        <li>Managing rate limits and optimizing token usage</li>
        <li>Ensuring appropriate content filtering for a broad audience</li>
        <li>Fine-tuning prompts to get consistent, high-quality responses</li>
    </ul>
    
    <h3>Results and Learnings</h3>
    <p>The integration of Gemini API has significantly enhanced user engagement in Breezy. Users can have meaningful interactions with the AI, receive personalized assistance, and enjoy a more dynamic experience.</p>
    
    <p>If you're considering using Gemini API in your projects, I highly recommend exploring its capabilities. The documentation is comprehensive, and the results can truly elevate your application's functionality.</p>
    """,
    'img/blog/gemini-api.jpg',
)

# Check if blog posts already exist
blog_count = db.execute('SELECT COUNT(*) as count FROM BlogPost').fetchone()['count']
if blog_count == 0:
    print("Adding blog posts...")
    db.execute('''
    INSERT INTO BlogPost (title, slug, content, image)
    VALUES (?, ?, ?, ?)
    ''', blog_post)
    
    db.execute('''
    INSERT INTO BlogPost (title, slug, content, image)
    VALUES (?, ?, ?, ?)
    ''', blog_post2)
else:
    print(f"Skipping blog posts (already have {blog_count} entries)")

# Create an admin user if not exists
admin_exists = db.execute('SELECT COUNT(*) as count FROM User WHERE is_admin = 1').fetchone()['count']
if admin_exists == 0:
    print("Creating admin user...")
    db.execute(
        'INSERT INTO User (username, password, is_admin) VALUES (?, ?, 1)',
        ('admin', generate_password_hash('admin'))
    )
else:
    print("Admin user already exists")

# Commit changes
db.commit()
db.close()

print("Database successfully seeded with portfolio data!") 