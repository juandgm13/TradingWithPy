# CLAUDE.md

This file provides guidance to Claude Code (claude.ai/code) when working with code in this repository.

## Project Overview

TradingWithPy es una aplicación de escritorio de trading construida con PyQt5 que integra múltiples exchanges (Binance, Alpaca) con gráficos en tiempo real, indicadores técnicos y un sistema de estrategias automatizadas.

## Running the Application

```bash
# Instalar dependencias
pip install -r requirements.txt

# Ejecutar la aplicación
python main.py
```

## Testing

```bash
# Ejecutar tests
pytest app/test/
```

## Configuration

### Environment Variables (.env)
El proyecto usa variables de entorno para las API keys:
- `BINANCE_API_KEY` / `BINANCE_API_SECRET`: Binance producción
- `BINANCE_API_KEY_TEST` / `BINANCE_API_SECRET_TEST`: Binance testnet
- `ALPACA_API_KEY` / `ALPACA_API_SECRET`: Alpaca producción
- `ALPACA_API_KEY_TEST` / `ALPACA_API_SECRET_TEST`: Alpaca paper trading

### Configuration File (app/utils/config/config.json)
Parámetros principales:
- `num_candles`: Número de velas a mostrar
- `indicators_period`: Período para indicadores (RSI, etc.)
- `timer_interval_ms`: Intervalo de actualización en milisegundos
- `enable_test_trading`: true para testnet/paper trading
- `email_notifications`: Configuración para notificaciones por email

## Architecture

### API Layer (app/api/)
**api_manager.py**: Facade pattern que gestiona múltiples APIs de exchanges. Inicializa clientes según el modo test/producción y proporciona una interfaz unificada.

**Implementations**: `binance_api.py` y `alpaca_api.py` implementan las mismas operaciones (get_candlestick_data, get_trading_symbols, etc.) pero adaptadas a cada exchange.

### Strategy System (app/strategies/)
**strategy_manager.py**: Registra y ejecuta estrategias de trading de forma modular.

**strategies.py**: Implementaciones de estrategias (actualmente Three-Screen Strategy de Alexander Elder). Cada estrategia hereda de `Strategy_class` y debe implementar `execute()`.

**Three-Screen Strategy**: Analiza el mercado en tres timeframes (largo, medio, corto) usando:
- Screen 1 (largo plazo): MACD + EMA 50/200 para identificar tendencia general
- Screen 2 (medio plazo): RSI + Bollinger Bands para detectar correcciones
- Screen 3 (corto plazo): EMAs 9/21 para señales de entrada

### Indicators (app/utils/indicators.py)
**IndicatorCalculator**: Clase estática con métodos para calcular:
- SMA, EMA
- Bollinger Bands
- RSI
- MACD (línea MACD, línea de señal, histograma)

Todos los métodos aceptan `closing_prices` como lista de floats.

### UI Layer (app/ui/)
**windows.py**: MainWindow es la ventana principal. Usa `DataUpdateWorker` (QThread) para actualizar datos en background sin bloquear la UI.

**tabs_definition.py**: Define TradingViewTab (gráficos con indicadores), OrdersTab (order book + órdenes abiertas), BalanceTab (balance de cuenta).

**charts.py**: Widgets de gráficos usando pyqtgraph (candlestick, volumen, profundidad, RSI).

### Utilities (app/utils/)
**config_loader.py**: ConfigLoader para cargar `config.json`.

**logger.py**: Logger configurado para la aplicación.

**symbol_info.py**: SymbolInfo dataclass con información de símbolos de trading.

**GmailSender.py**: Envío de notificaciones por email (Gmail).

## Important Patterns

### Threading Pattern
La UI usa `DataUpdateWorker` (QThread) para operaciones de API en background. Emite señales pyqt (`update_tab`, `error_occurred`) para comunicarse con la UI thread.

### API Abstraction
`APIManager` selecciona dinámicamente entre exchanges y modos test/producción. Nuevos exchanges deben implementar la misma interfaz que BinanceAPI/AlpacaAPI.

### Configuration-Driven
Indicadores y comportamiento se configuran vía `config.json`, no hardcodeados. Permite ajustar períodos, intervalos y features sin modificar código.

## Data Flow

1. **MainWindow** actualiza cada `timer_interval_ms`
2. **DataUpdateWorker** ejecuta en background:
   - Llama a `api_manager` según la tab seleccionada
   - Emite señal `update_tab` con los datos
3. **Tab específica** recibe datos y actualiza gráficos/tablas
4. **Strategies** se ejecutan periódicamente, analizan datos de mercado y generan señales

## Adding New Features

### New Exchange
1. Crear `app/api/nueva_api.py` implementando los métodos de BinanceAPI
2. Agregar en `APIManager._init_*()` y `api_clients` dict
3. Agregar variables de entorno en `.env`

### New Strategy
1. Heredar de `Strategy_class` en `strategies.py`
2. Implementar método `execute(api_manager)` que retorna lista de señales
3. Registrar en `StrategyManager` (ver `windows.py:110-122`)

### New Indicator
1. Agregar método estático en `IndicatorCalculator`
2. Recibir `closing_prices` o datos de velas
3. Retornar lista de valores calculados
