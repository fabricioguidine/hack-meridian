# Decentralized Badge System (POAP-like on Soroban)

## 📖 Project Description

This project is a **decentralized badge system** built on the **Soroban smart contracts platform (Stellar network)**.  
It enables organizers to create **verifiable digital badges** (similar to NFTs) for events and online courses.  
Participants who attend an event or complete a course receive a **unique badge that proves their participation**.

The solution also incorporates **gamification and rewards**: collecting badges can unlock achievements, incentives, or recognition — motivating users to join more events and courses.  

- **Badges** are immutable, verifiable, and stored **on-chain**.  
- **Metadata** (name, description, images) is referenced via **IPFS**.  

This combination ensures both **trust** (blockchain verification) and **scalability** (off-chain content storage).

### ✅ In short, the project provides:

- **Transparency** → All participation is verifiable on-chain.  
- **Engagement** → Users are rewarded with badges and gamified incentives.  
- **Simplicity** → Organizers easily create events, mint badges, and track participants.  

---

## 🛠 Technologies Used

- **Rust + Soroban SDK** → Smart contract development (events, badges, storage).  
- **Stellar Soroban** → Blockchain network for deploying and executing contracts.  
- **IPFS** → Decentralized storage for metadata (badge details, images).  
- **Stellar/Soroban SDKs (frontend integration)** → Reading/writing data via wallets and DApps.  
- **Optional Python Backend** → For indexing, caching, and providing an API layer (not mandatory).  
- **Wallet Integration** → Enables users to claim badges and view them securely.
- **JavaScript** → Enables user interaction to the system.

---

## 📊 System Flow (simplified)

```mermaid
flowchart LR
    A[👩 Organizer] -->|Create Event / Mint Badge| B[(📜 Soroban Contract)]
    B --> C[🌐 IPFS Metadata]
    B --> D[👤 User Wallet]
    D --> E[💻 Frontend / DApp]
    E -->|Display| D
