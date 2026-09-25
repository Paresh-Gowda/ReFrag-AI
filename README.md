# AI-Assisted Intelligent Data Recovery and Digital Evidence Reconstruction

This project is a cybersecurity and AI-based digital evidence recovery platform designed to assist in identifying, reconstructing, classifying, and prioritizing recoverable information from damaged, deleted, fragmented, or partially corrupted storage data. The system is designed to go beyond traditional file recovery by analyzing recovered fragments, identifying relationships between them, evaluating reconstruction possibilities, and presenting meaningful recovery insights through an intuitive dashboard.

The frontend has been developed using React and Vite with a modern dark-themed forensic dashboard interface. The application currently includes a Dashboard, Scan Data, Fragments, Evidence, and Analytics sections, along with a persistent sidebar and top navigation. React Router is used for client-side navigation so users can switch between sections without full-page browser refreshes. The interface has also been structured with reusable components and responsive styling to provide a clean foundation for integrating the backend forensic processing and AI/ML pipeline.

The project follows a modular architecture so that the frontend can later communicate with the backend through APIs. The planned system will connect the user interface with data scanning, file-type detection, fragment relationship analysis, reconstruction, integrity analysis, and AI-assisted classification and prioritization modules. The current implementation focuses on establishing a polished and functional frontend foundation that can be extended with the forensic engine, machine learning models, database, and real-time recovery results.

## Project Structure

```text
paresh-portfolio/
│
├── public/
│   └── ...
│
├── src/
│   ├── assets/
│   │   └── ...
│   │
│   ├── components/
│   │   ├── Sidebar.jsx
│   │   ├── Topbar.jsx
│   │   └── ...
│   │
│   ├── pages/
│   │   ├── Dashboard.jsx
│   │   ├── ScanData.jsx
│   │   ├── Fragments.jsx
│   │   ├── Evidence.jsx
│   │   └── Analytics.jsx
│   │
│   ├── App.jsx
│   ├── App.css
│   ├── index.css
│   └── main.jsx
│
├── .gitignore
├── package.json
├── package-lock.json
├── vite.config.js
└── README.md
```