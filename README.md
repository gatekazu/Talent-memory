# Memorama Arcade Retro

Juego de memoria estilo arcade retro con leaderboard compartido en red WiFi.
Desarrollado para **TALENT LAND 2026** | Powered by Kiro with AWS México.

---

## Iniciar el juego

**Windows:** Haz doble clic en `start.bat`.
**Linux/Mac:** Ejecuta `./start.sh`.

Esto levanta un servidor local en tu red WiFi y abre el juego automáticamente en el navegador.

Una vez abierto, verás el botón **⬛ QR MÓVIL** en la esquina superior derecha del menú principal.
Haz clic para mostrar el código QR — cualquier teléfono en la misma red WiFi puede escanearlo para jugar.

## Reiniciar el servidor

Si el servidor deja de responder, haz doble clic en `restart-server.bat`.
Cierra el proceso anterior y levanta uno nuevo automáticamente.

## Requisitos

- Python 3 instalado ([python.org](https://python.org))
- PC y teléfonos en la misma red WiFi

## Sin servidor (modo local)

Si no necesitas jugar desde el teléfono, abre `index.html` directamente en Chrome, Edge o Firefox.
El juego funciona sin servidor — solo el QR móvil requiere que estés sirviendo desde HTTP.

## Leaderboard (scores)

Los puntajes se guardan en `scores.json` (excluido del repo).
Copia `scores.example.json` como `scores.json` para iniciar con datos de ejemplo:

```bash
cp scores.example.json scores.json
```

---

## Estrategia de ramas

```
main
├── prod                  ← código estable en producción
│   └── feature/<nombre>  ← nuevas features para prod
└── devops                ← infraestructura, scripts, CI/CD
    └── feature/<nombre>  ← features de devops/infra
```

### Flujo de trabajo

| Rama | Propósito |
|------|-----------|
| `main` | Base inicial del proyecto |
| `prod` | Código desplegado / estable |
| `prod/feature/<nombre>` | Desarrollo de nuevas funcionalidades |
| `devops` | Scripts, automatización, CI/CD |
| `devops/feature/<nombre>` | Mejoras de infraestructura |

**Para una nueva feature de juego:**
```bash
git checkout prod
git checkout -b feature/nombre-feature
# ... desarrollar ...
git push origin feature/nombre-feature
# Abrir Pull Request → prod
```

**Para una nueva feature de devops:**
```bash
git checkout devops
git checkout -b devops/feature/nombre-feature
# ... desarrollar ...
git push origin devops/feature/nombre-feature
# Abrir Pull Request → devops
```

---

TALENT LAND 2026 | Powered by Kiro with AWS México | Autor: Kazu Shiraki
