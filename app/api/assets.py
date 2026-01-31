"""
Endpoint para listar activos soportados

Este endpoint proporciona la lista de activos disponibles
para que el frontend pueda llenar los dropdowns de selección.
"""

from fastapi import APIRouter
from app.schemas.patterns import AssetsListResponse, AssetInfo

router = APIRouter(prefix="/api", tags=["Activos"])

# Lista de activos soportados (MVP)
# Estos son los activos que el frontend puede mostrar en los dropdowns
SUPPORTED_ASSETS = {
    "crypto": [
        {"symbol": "BTCUSDT", "name": "Bitcoin"},
        {"symbol": "ETHUSDT", "name": "Ethereum"},
    ],
    "stocks": [
        {"symbol": "AAPL", "name": "Apple Inc."},
        {"symbol": "TSLA", "name": "Tesla Inc."},
        {"symbol": "MSFT", "name": "Microsoft Corporation"},
        {"symbol": "GOOGL", "name": "Alphabet Inc. (Google)"},
    ],
    "cedears": [
        {"symbol": "AAPL.BA", "name": "Apple CEDEAR"},
        {"symbol": "TSLA.BA", "name": "Tesla CEDEAR"},
        {"symbol": "MSFT.BA", "name": "Microsoft CEDEAR"},
    ]
}


@router.get(
    "/assets",
    response_model=AssetsListResponse,
    summary="Listar activos soportados",
    description=(
        "Este endpoint devuelve la lista de activos soportados por mercado. "
        "El frontend puede usar esta información para llenar los dropdowns de selección. "
        "Incluye criptomonedas, acciones y CEDEARs disponibles para análisis."
    )
)
async def listar_activos():
    """
    Lista todos los activos soportados por la aplicación, organizados por mercado.
    
    **Respuesta:**
    - `crypto`: Lista de criptomonedas disponibles (ej: BTCUSDT, ETHUSDT)
    - `stocks`: Lista de acciones disponibles (ej: AAPL, TSLA, MSFT)
    - `cedears`: Lista de CEDEARs disponibles (ej: AAPL.BA, TSLA.BA)
    
    Cada activo incluye:
    - `symbol`: Símbolo técnico del activo (para usar en otros endpoints)
    - `name`: Nombre descriptivo del activo (para mostrar en el frontend)
    
    **Ejemplo de respuesta:**
    ```json
    {
      "crypto": [
        {"symbol": "BTCUSDT", "name": "Bitcoin"},
        {"symbol": "ETHUSDT", "name": "Ethereum"}
      ],
      "stocks": [
        {"symbol": "AAPL", "name": "Apple Inc."},
        {"symbol": "TSLA", "name": "Tesla Inc."},
        {"symbol": "MSFT", "name": "Microsoft Corporation"},
        {"symbol": "GOOGL", "name": "Alphabet Inc. (Google)"}
      ],
      "cedears": [
        {"symbol": "AAPL.BA", "name": "Apple CEDEAR"},
        {"symbol": "TSLA.BA", "name": "Tesla CEDEAR"},
        {"symbol": "MSFT.BA", "name": "Microsoft CEDEAR"}
      ]
    }
    ```
    
    **Uso en frontend:**
    El frontend puede consumir este endpoint al cargar para:
    1. Llenar dropdowns de selección de activos
    2. Validar que un símbolo está soportado
    3. Mostrar nombres amigables en lugar de símbolos técnicos
    
    **Ejemplo de uso en JavaScript:**
    ```javascript
    const response = await fetch('http://localhost:8000/api/assets');
    const data = await response.json();
    
    // Llenar dropdown de crypto
    data.crypto.forEach(asset => {
      const option = document.createElement('option');
      option.value = asset.symbol;
      option.text = asset.name;
      cryptoDropdown.appendChild(option);
    });
    ```
    """
    return AssetsListResponse(
        crypto=[AssetInfo(**asset) for asset in SUPPORTED_ASSETS["crypto"]],
        stocks=[AssetInfo(**asset) for asset in SUPPORTED_ASSETS["stocks"]],
        cedears=[AssetInfo(**asset) for asset in SUPPORTED_ASSETS["cedears"]]
    )
