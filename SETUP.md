# Hermes Immortal — Setup Instructions

## 1. Add SSH Key to GitHub

Copy this key and add it at https://github.com/settings/keys:

```
ssh-ed25519 AAAAC3NzaC1lZDI1NTE5AAAAIA+0KyRyuVRhZdzkFhWOeSSrPzcXH8lpSLmHaEK2wSLB smrai@cognitiafury
```

## 2. Create the Repo on GitHub

```bash
gh repo create cognitia-ai/hermes-immortal --public --description "Hermes Immortal Agent Stack"
```
Or create manually at https://github.com/new

## 3. First Push

```bash
cd ~/hermes-immortal
git branch -m main
git add -A
git commit -m "Initial commit: Hermes immortal stack"
git push -u origin main
```

## 4. Verify Auto-Backup

The cron job runs daily at midnight. Check logs:
```bash
cat ~/hermes-immortal/.backup-log | tail -20
```
