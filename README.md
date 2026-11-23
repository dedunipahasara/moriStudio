# Mori Studio

### AI-Powered Image Generation and Creative Studio

Mori Studio is an AI-powered creative platform designed to transform text prompts into visually appealing digital images. It combines modern web technologies with AI-based image generation and image-processing capabilities to provide users with a creative environment for generating, managing, and enhancing digital artwork.

The platform brings together a user-friendly frontend, backend services, and an AI engine to support image generation workflows and creative operations.

---

## Preview

<!-- Add your main application screenshot here -->
<img width="1906" height="941" alt="Screenshot from 2026-11-23 12-41-22" src="https://github.com/user-attachments/assets/71c77160-9edf-43f6-bad9-0863555954e5" />


*Replace this image with a screenshot of the Mori Studio homepage.*

---

## Key Features

- **AI Image Generation** – Generate images using AI-powered diffusion and generation workflows.
- **Prompt Processing** – Process text prompts and prepare them for AI image generation.
- **Image Processing** – Support image encoding, preprocessing, optimization, and enhancement operations.
- **User Authentication** – Backend authentication and user account management.
- **Asset Management** – Manage generated images and user-related assets.
- **File Upload Management** – Handle image and file upload operations.
- **Background Processing** – Support image generation tasks through background workers.
- **AI Model Support** – Includes AI inference, prediction, training, and model-related components.
- **API Integration** – Connect frontend functionality with backend and AI services.

---

## Application Screenshots

Add your actual application screenshots to `docs/images/` and use the following image paths.

### 1. Home Page
<img width="1906" height="941" alt="Screenshot from 2026-11-23 12-41-22" src="https://github.com/user-attachments/assets/f0267356-5070-4bdc-a676-d49adda5f1c2" />

### 2. Aboutus
<img width="1904" height="904" alt="Screenshot from 2026-11-24 00-21-18" src="https://github.com/user-attachments/assets/8dd052a0-5d2b-4f7b-8bd0-eaeab43a7f9e" />

### 3. Create Account
<img width="1919" height="912" alt="Screenshot from 2026-11-24 00-22-51" src="https://github.com/user-attachments/assets/918f447d-825b-465e-ae96-8b601cbb5784" />

### 4.Forget Password
<img width="1919" height="912" alt="Screenshot from 2026-11-24 00-22-51" src="https://github.com/user-attachments/assets/011a7261-c4e2-45a5-8f6e-d7d027e42f08" />

### 5. Image Processing
<img width="1695" height="958" alt="Screenshot from 2026-11-23 14-17-40" src="https://github.com/user-attachments/assets/809dc150-2600-43f8-8074-75bdb3f6a43a" />

### 6. Image genrerating
<img width="1693" height="958" alt="Screenshot from 2026-11-23 14-18-45" src="https://github.com/user-attachments/assets/557eb052-5dae-454a-b245-e0a11e8c53c8" />

---

## Technology Stack

The project includes the following technology areas:

| Component | Technologies / Tools |
|---|---|
| Frontend | Web-based application |
| Backend | Backend application and REST API services |
| Database | Prisma ORM and database migrations |
| AI Engine | Python-based AI components |
| AI Processing | Diffusion, inference, prediction and image processing |
| Development | Git and GitHub |

*Update this section with the exact framework and database versions used in your project.*

---

## Project Structure

```text
moriStudio/
│
├── frontend/              # Frontend application
│
├── backend/               # Backend API and services
│   ├── prisma/            # Database schema and migrations
│   ├── src/               # Backend source code
│   └── tests/             # Backend tests
│
├── ai-engine/             # AI image generation engine
│   ├── app/               # AI application and API
│   ├── services/          # AI generation services
│   ├── models/            # AI model components
│   ├── datasets/          # AI datasets
│   └── scripts/           # Training and generation scripts
│
├── docs/                  # Project documentation
│   └── images/            # README screenshots
│
├── .gitignore
└── README.md
```

*The structure above is a simplified overview. Adjust folder names to match the actual repository.*

---

## Getting Started

### Prerequisites

Install the required development tools before running the project:

- Git
- Node.js and npm
- Python
- Required database system
- Python dependencies for the AI engine

### 1. Clone the Repository

```bash
git clone https://github.com/dedunipahasara/moriStudio.git
```

### 2. Navigate to the Project

```bash
cd moriStudio
```

### 3. Install Dependencies

Install the frontend and backend dependencies using the package manager configured in each project directory.

```bash
cd frontend
npm install
```

```bash
cd ../backend
npm install
```

### 4. Configure Environment Variables

Create the required `.env` files based on the environment configuration examples provided in the project.

Do not upload real credentials, API keys, database passwords, or other sensitive information to GitHub.

### 5. Set Up the AI Engine

Navigate to the AI engine directory and install the Python dependencies specified in its requirements file.

```bash
cd ../ai-engine
pip install -r requirements.txt
```

### 6. Run the Application

Start the frontend, backend, and AI services using their respective development commands and configured environment settings.

*Refer to the individual project configurations for the exact startup commands.*

---

## Development Highlights

Mori Studio is organized into multiple development areas:

- AI image generation and diffusion processing.
- Image preprocessing and encoding.
- AI model inference and prediction.
- Prompt processing and text encoding.
- Model training and generation scripts.
- Backend authentication and user management.
- Database schema and migration management.
- Image uploads, asset management, and background processing.
- API schemas, endpoints, and testing.

---

## Future Improvements

- Improve AI image generation quality and performance.
- Introduce additional image enhancement capabilities.
- Improve the user experience and generation workflow.
- Expand AI model capabilities.
- Add more creative tools and image customization options.

---

## Author

**Thamasha Deduni Pahasara**

GitHub: [@dedunipahasara](https://github.com/dedunipahasara)

---

## License

This project is distributed under the license included in this repository. Please refer to the [LICENSE](LICENSE) file for details.

---

<p align="center">
  <strong>Mori Studio – Create. Imagine. Generate.</strong>
</p>
