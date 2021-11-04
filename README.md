# PyNanoKontrol4Linux

## Developing

Install dependencies:

```bash
./deploy/prepare-deploy.sh
```

Run application

```bash
source ./venv/activate
npx nodemon --exec python3 src/main.py config/nanokontrol-example.yml
```
