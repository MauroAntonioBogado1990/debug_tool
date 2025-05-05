from odoo import models, fields, api
import logging

_logger = logging.getLogger(__name__)

class ToolDebug(models.Model):
    _name = 'debug.tool'

    model_name = fields.Char(
        string='Nombre del Modelo', 
        required=True, 
        help="Escribe el nombre técnico del modelo, por ejemplo, 'res.partner'"
    )
    record_id = fields.Integer(
        string='ID del Registro', 
        help="Especifica el ID del registro para depurar"
    )
    field_name = fields.Char(
        string='Ruta del Campo', 
        help="Escribe el nombre del campo o ruta (por ejemplo, 'move_id.invoice_line_ids.price_total')"
    )
    function_name = fields.Char(
        string='Nombre de la Función', 
        help="Escribe el nombre de la función a ejecutar"
    )
    output = fields.Text(
        string='Salida', 
        readonly=True, 
        help="Resultado de la operación"
    )

    def execute_debug(self):
        """ Ejecuta la lógica de depuración y devuelve los resultados """
        try:
            # Verificar si el modelo es válido
            model = self.env[self.model_name]
            output = "Resultados:\n"
            
            # Obtener el registro específico (si el ID es proporcionado)
            record = model.browse(self.record_id) if self.record_id else None

            if record and not record.exists():
                self.output = "Error: El registro con el ID proporcionado no existe."
                return

            if self.field_name:  # Inspeccionar campos o rutas
                output += f"- Ruta del Campo '{self.field_name}':\n"
                if record:  # Campo o relación en un registro específico
                    value = self._get_relational_value(record, self.field_name)
                    output += f"  ID {record.id}: {value}\n"
                else:  # Campo o relación en todos los registros
                    for obj in model.search([]):
                        value = self._get_relational_value(obj, self.field_name)
                        output += f"  ID {obj.id}: {value}\n"

            if self.function_name:  # Ejecutar la función
                output += f"\n- Resultado de la función '{self.function_name}':\n"
                if record:  # Función en un registro específico
                    func = getattr(record, self.function_name, None)
                    if callable(func):
                        result = func()
                        output += f"  ID {record.id}: {result}\n"
                    else:
                        output += f"  ID {record.id}: La función no existe o no es ejecutable.\n"
                else:  # Función en todos los registros
                    for obj in model.search([]):
                        func = getattr(obj, self.function_name, None)
                        if callable(func):
                            result = func()
                            output += f"  ID {obj.id}: {result}\n"
                        else:
                            output += f"  ID {obj.id}: La función no existe o no es ejecutable.\n"

            self.output = output
        except Exception as e:
            _logger.error("Error ejecutando el debug: %s", e)
            self.output = f"Error: {str(e)}"

    def _get_relational_value(self, record, field_path):
        """
        Navega por relaciones para obtener el valor de subcampos.

        Ejemplo:
        - field_path="move_id.invoice_line_ids.price_total"
        """
        try:
            fields = field_path.split('.')  # Divide la ruta (relación -> campo)
            value = record
            for field in fields:
                value = getattr(value, field, "Campo/Relación no encontrado")
                if isinstance(value, models.BaseModel):  # Si es una relación, continúa
                    value = value  # Mantén el objeto navegable
                elif isinstance(value, list):
                    value = [str(v) for v in value]  # Convierte listas en texto
                else:
                    break  # Si no es relacional, detente
            return value
        except Exception as e:
            _logger.error("Error obteniendo valor relacional: %s", e)
            return f"Error accediendo al campo '{field_path}': {str(e)}"