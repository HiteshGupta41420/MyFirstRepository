
# Invoice Processing Platform (Mini-Project)

End-to-end demo using FastAPI backend, Python worker, PostgreSQL, Kubernetes, Helm, and Argo CD (GitOps).

## Prerequisites
- Docker Desktop with Kubernetes enabled
- kubectl, Helm
- (Recommended) ingress-nginx controller

## 0) Install ingress-nginx (if not already)
```bash
helm repo add ingress-nginx https://kubernetes.github.io/ingress-nginx
helm upgrade --install ingress-nginx ingress-nginx/ingress-nginx -n ingress-nginx --create-namespace
```

## 1) Build images
```bash
docker build -t invoice-backend:local ./backend
docker build -t invoice-worker:local ./worker
```

## 2) Deploy via Helm
```bash
kubectl create ns apps || true
helm upgrade --install invoice ./helm/invoice-platform -n apps
kubectl -n apps get pods
```

## 3) Test the API
```bash
curl http://invoice.127.0.0.1.nip.io/health
curl -X POST http://invoice.127.0.0.1.nip.io/invoices -H "Content-Type: application/json" -d '{"customer":"Hitesh","amount":1000}'
kubectl -n apps logs deploy/invoice-invoice-platform-worker -f
```

## 4) Install Argo CD
```bash
kubectl create ns argocd
kubectl apply -n argocd -f https://raw.githubusercontent.com/argoproj/argo-cd/stable/manifests/install.yaml
kubectl -n argocd get pods
# UI access (new terminal):
kubectl -n argocd port-forward svc/argocd-server 8080:443
# Initial admin password:
kubectl -n argocd get secret argocd-initial-admin-secret -o jsonpath="{.data.password}" | base64 -d; echo
# Open https://localhost:8080 (user: admin, password: above)
```

## 5) Push this repo and let Argo CD manage it
- Create a GitHub repository (e.g., https://github.com/<your-username>/invoice-platform)
- Commit and push this folder.
- Edit `argo/application.yaml` and replace the `repoURL` with your repo.
```bash
kubectl apply -f argo/application.yaml
```
- In Argo CD UI, you should see the `invoice-platform` app syncing to the cluster.

## 6) Useful
- Create more invoices and watch the worker complete them.
- Scale backend/worker via Helm values and commit to Git to observe GitOps sync.
