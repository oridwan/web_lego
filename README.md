# Hosting LEGO-sp2 on Render.com and Previewing Locally

This guide explains how to host the **LEGO-sp2** application on Render.com and how to preview the application locally before deployment.

---

## Hosting on Render.com

### Render Deployment Settings

The application is hosted on Render.com with the following settings:

- **Service Name**: LEGO-sp2
- **Repository**: [web_lego](https://github.com/oridwan/web_lego)
- **Branch**: `master`
- **Build Command**: `pip install -r requirements.txt`
- **Start Command**: `./start.sh`
  
### Steps to Deploy on Render.com

1. **Connect Repository**:
   - Log in to your Render.com account.
   - Connect the GitHub repository: [web_lego](https://github.com/oridwan/web_lego).

2. **Configure Deployment**:
   - Set the branch to `master`.
   - Specify the build command:
     ```bash
     pip install -r requirements.txt
     ```
   - Specify the start command:
     ```bash
     ./start.sh
     ```

3. **Deploy**:
   - Render will automatically build and deploy the application.
   - Access the application at [https://lego-crystal.onrender.com](https://lego-crystal.onrender.com).

---

## Previewing Locally

### Prerequisites

1. Ensure Python and ASE (Atomic Simulation Environment) are installed.
2. Verify that the [lego-sp2.db](https://github.com/oridwan/web_lego/blob/master/lego-sp2.db) database file is present in the project directory.

### Steps to Preview Locally

1. **Clone the Repository**:
   - Open a terminal and clone the repository:
     ```bash
     git clone https://github.com/oridwan/web_lego.git
     cd web_lego
     ```

2. **Install Dependencies**:
   - Install the required Python packages:
     ```bash
     pip install -r requirements.txt
     ```

3. **Run the Application**:
   - Start the ASE web server locally:
     ```bash
     ase db lego-sp2.db -w
     ```
   - Access the application at `http://localhost:5000`.

4. **Preview with JSmol Integration**:
   - Ensure the `jsmol.zip` file is present in the project directory.
   - Run the [start.sh](http://_vscodecontentref_/1) script to automatically extract JSmol and start the server:
     ```bash
     ./start.sh
     ```
   - Open `http://localhost:5000` in your browser to preview the application with JSmol integration.

---

## Contact

For any questions or issues, please contact the owner at **ogridwan@gmail.com**.
