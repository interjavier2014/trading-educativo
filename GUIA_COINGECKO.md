# Guía de prueba: CoinGecko como proveedor crypto

## Resumen

CoinGecko es el proveedor **principal** de datos crypto para producción. Binance devuelve 451 (restricted location) en Railway y otros entornos cloud.

- **Primario:** CoinGecko (funciona globalmente)
- **Secundario:** Binance (si CoinGecko falla)
- **Fallback:** JSON educativo con `DATA_TEMPORARILY_UNAVAILABLE` si ambos fallan

---

## URLs listas para probar

### Local (localhost:8000)

```
# Bitcoin - 1h
http://localhost:8000/api/analysis?market=crypto&symbol=BTCUSDT&timeframe=1h

# Ethereum - 4h
http://localhost:8000/api/analysis?market=crypto&symbol=ETHUSDT&timeframe=4h

# Solana - 1d
http://localhost:8000/api/analysis?market=crypto&symbol=SOLUSDT&timeframe=1d

# BNB
http://localhost:8000/api/analysis?market=crypto&symbol=BNBUSDT&timeframe=1h

# Ripple (XRP)
http://localhost:8000/api/analysis?market=crypto&symbol=XRPUSDT&timeframe=1h
```

### Producción (reemplazar BASE_URL por tu dominio)

```
{BASE_URL}/api/analysis?market=crypto&symbol=BTCUSDT&timeframe=1h
{BASE_URL}/api/analysis?market=crypto&symbol=ETHUSDT&timeframe=4h
{BASE_URL}/api/analysis?market=crypto&symbol=SOLUSDT&timeframe=1d
{BASE_URL}/api/analysis?market=crypto&symbol=BNBUSDT&timeframe=1h
{BASE_URL}/api/analysis?market=crypto&symbol=XRPUSDT&timeframe=1h
```

### Ejemplo Railway

```
https://tu-app.up.railway.app/api/analysis?market=crypto&symbol=BTCUSDT&timeframe=1h
```

---

## Símbolos soportados

| Símbolo   | CoinGecko ID | Nombre   |
|-----------|--------------|----------|
| BTCUSDT   | bitcoin      | Bitcoin  |
| ETHUSDT   | ethereum     | Ethereum |
| SOLUSDT   | solana       | Solana   |
| BNBUSDT   | binancecoin  | BNB      |
| XRPUSDT   | ripple       | Ripple   |

Símbolos desconocidos devuelven fallback educativo (no 500).

---

## Respuesta esperada (éxito)

```json
{
  "asset": "BTCUSDT",
  "market": "crypto",
  "timeframe": "1h",
  "precio_actual": 97234.56,
  "total_velas_analizadas": 96,
  "patrones_detectados": 1,
  "patrones": [...],
  "disclaimer_code": "DISCLAIMER"
}
```

---

## Respuesta fallback (fuentes externas no disponibles)

```json
{
  "asset": "BTCUSDT",
  "market": "crypto",
  "timeframe": "1h",
  "precio_actual": 0.0,
  "total_velas_analizadas": 0,
  "patrones_detectados": 0,
  "patrones": [],
  "disclaimer_code": "DISCLAIMER",
  "status_code": "DATA_TEMPORARILY_UNAVAILABLE",
  "message_code": "DATA_SOURCE_ERROR",
  "confidence": "LOW"
}
```

---

## Listar activos

```
GET /api/assets
```

Incluye todos los símbolos crypto soportados.

---

## Notas

- CoinGecko OHLC **no incluye volumen**; se usa `0` para compatibilidad.
- La API gratuita de CoinGecko tiene granularidad automática según `days`.
- El endpoint **nunca** devuelve 500 por problemas de fuentes externas.
