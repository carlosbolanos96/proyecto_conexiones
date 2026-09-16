# Proposal: Plataforma Doble Modo

## Intent

Organizar la arquitectura base de una app Django que conecta productores y consumidores con dos modos: restaurantes/delivery y agro/bodegas. La meta es un MVP simple y útil, con apps separadas por responsabilidad sin crear complejidad empresarial innecesaria.

## Scope

### In Scope
- Definir apps Django compartidas: `accounts`, `locations`, `orders`, `payments`, `notifications`.
- Definir apps del modo restaurantes: `restaurants`, `menus`, `delivery`.
- Definir apps del modo agro: `agro`, `warehouses`, `inventory`.
- Proponer modelo de usuario único con perfiles/roles: consumer, producer, courier, warehouse_manager.
- Mantener `core` para home, navegación inicial y páginas públicas.

### Out of Scope
- Implementar modelos, vistas, templates o migraciones.
- Integrar pagos reales, mapas reales, tracking en tiempo real o APIs externas.
- Resolver logística avanzada, comisiones, facturación o analítica.

## Capabilities

### New Capabilities
- `account-roles`: autenticación y perfiles por rol sobre un único usuario Django.
- `shared-commerce`: órdenes, estados, direcciones, pagos simulados y notificaciones.
- `restaurant-mode`: catálogo de restaurantes, menús, productos y despacho por courier.
- `agro-mode`: productores agro, bodegas, inventario, pedidos por cantidad y entrega/retiro.
- `project-structure`: estructura de apps Django, URLs, templates y responsabilidades por carpeta.

### Modified Capabilities
- None

## Approach

Usar un monolito Django modular: muchas apps pequeñas dentro del mismo proyecto, no microservicios. `accounts` concentra identidad y roles; cada modo agrega modelos específicos pero reutiliza órdenes, ubicaciones, pagos y notificaciones. Para MVP, usar SQLite, Django admin, templates server-side y pagos/notificaciones simulados.

Alternativa descartada: una app gigante `marketplace`, porque mezcla conceptos y dificulta aprender límites. También se descartan microservicios porque agregan infraestructura sin valor para esta etapa.

## Affected Areas

| Area | Impact | Description |
|------|--------|-------------|
| `conexiones/settings.py` | Modified | Registrar futuras apps del dominio. |
| `conexiones/urls.py` | Modified | Incluir rutas por app/modo. |
| `core/` | Modified | Mantener home y navegación pública. |
| `accounts/`, `locations/`, `orders/`, `payments/`, `notifications/` | New | Componentes compartidos. |
| `restaurants/`, `menus/`, `delivery/` | New | Modo restaurantes/delivery. |
| `agro/`, `warehouses/`, `inventory/` | New | Modo agro/bodegas. |

## Risks

| Risk | Likelihood | Mitigation |
|------|------------|------------|
| Demasiadas apps para un proyecto inicial | Med | Crear solo estructura mínima y modelos esenciales. |
| Roles confusos entre productor, restaurante y bodega | Med | Documentar perfiles y permisos antes de implementar. |
| Órdenes compartidas demasiado genéricas | Med | Usar campos comunes y detalles por modo cuando haga falta. |

## Rollback Plan

Como esta fase solo planifica, revertir eliminando `openspec/changes/platforma-doble-modo/proposal.md`. En implementación futura, cada app se podrá revertir removiéndola de `INSTALLED_APPS`, URLs y migraciones no aplicadas.

## Dependencies

- Django 6.1.1 existente.
- Specs y diseño SDD antes de implementar código.

## Success Criteria

- [ ] La arquitectura separa claramente componentes compartidos y específicos por modo.
- [ ] La fase de specs puede crear documentos desde las capacidades listadas.
- [ ] El diseño resultante sigue siendo viable para un MVP estudiantil.
