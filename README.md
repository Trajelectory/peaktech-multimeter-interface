# 🔌 PeakTech 2025 Monitor

🚀 **Interface graphique et serveur Web pour le multimètre PeakTech 2025**

---

## 📜 Description

Ce projet permet d'afficher et de surveiller en **temps réel** les mesures d'un multimètre **PeakTech 2025** via une interface **Tkinter** et un serveur **Flask WebSocket**.

🔹 **Affichage des valeurs en direct** 📊  
🔹 **Graphique dynamique des mesures** 📈  
🔹 **Serveur Flask pour affichage web** 🌐  
🔹 **Connexion au multimètre via port série** 🔗  

---

## 🛠️ Installation des dépendances

Avant d'exécuter le projet, installez les bibliothèques nécessaires :

```bash
pip install tkinter matplotlib pyserial flask flask_socketio
```

---

## 📂 Structure du projet

```
📁 PeakTech_2025_Monitor
├── 📝 app.py                # Lance l'application Tkinter
├── 🖥️ peaktech_gui.py       # Interface graphique avec Tkinter
├── ⚙️ peaktech_utils.py     # Décodage des données et serveur Flask
```

---

## ▶️ Utilisation

### 1️⃣ Lancer l'application GUI 🖥️

```bash
python app.py
```

### 2️⃣ Connecter le multimètre 📡
   - Sélectionnez le **port série** 🔌
   - Cliquez sur **Connect** ✅
   - Les données apparaissent **en temps réel** 📊

### 3️⃣ Activer le widget Web 🌍 (facultatif)
   - Cliquez sur le bouton **Widget** ⚡
   - Ouvrez `http://127.0.0.1:5000/` dans un navigateur 🌐

### 4️⃣ Déconnecter le multimètre ❌
   - Cliquez sur **Disconnect** 🔴

---

## 🧩 Explication du Code

### 🔹 `app.py`

- Initialise **l'interface Tkinter** 🖥️
- Vérifie la **présence de la police** `Digital-7`
- Lance l'instance de `PeakTechApp` 🎛️

### 🔹 `peaktech_gui.py`

- Interface **graphique interactive** avec `tkinter` 🎨
- **Connexion au multimètre** et **lecture des données** 🔍
- **Affichage en direct** et **graphe dynamique** 📈
- **Lance un serveur Flask** en arrière-plan 🌍

### 🔹 `peaktech_utils.py`

- **Décodage des trames série** du multimètre 🔢
- **Serveur Flask WebSocket** pour affichage en temps réel 🚀
- Utilise **`flask_socketio`** pour mettre à jour l'affichage 📡

---

## ⚠️ Notes Importantes

⚡ **Le multimètre doit être configuré avec un baudrate de 2400.**
🔍 **Vérifiez que le port série est correct et accessible.**
🎨 **La police `Digital-7` est recommandée pour un meilleur affichage.**

---

## ✨ Auteurs

Ce projet a été développé pour faciliter la lecture et la visualisation des **données du multimètre PeakTech 2025** 📡⚡.

💡 **Améliorations et contributions bienvenues !** 🚀

