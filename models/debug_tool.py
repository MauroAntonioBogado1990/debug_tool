from odoo import models, fields, api
import logging
import inspect  # Nuevo: para obtener la ubicación del archivo

_logger = logging.getLogger(__name__)

class ToolDebug(models.Model):
    _name = 'debug.tool'

    model_name = fields.Char(string='Nombre del Modelo', required=True)
    record_id = fields.Integer(string='ID del Registro')
    field_name = fields.Char(string='Ruta del Campo')
    function_name = fields.Char(string='Nombre de la Función')
    output = fields.Text(string='Salida', readonly=True)

    def execute_debug(self):
        """ Ejecuta la lógica de depuración con trazabilidad y muestra la ubicación del código fuente """
        try:
            model = self.env[self.model_name]
            trace_log = []  # Almacena el rastro de ejecución
            output = "Resultados:\n"

            # Obtener el registro específico
            record = model.browse(self.record_id) if self.record_id else None

            if record and not record.exists():
                self.output = "Error: El registro con el ID proporcionado no existe."
                return

            if self.field_name:
                trace_log.append(f"Inspección del campo: {self.field_name}")
                output += f"- Ruta del Campo '{self.field_name}':\n"
                
                if record:
                    value = self._get_relational_value(record, self.field_name, trace_log)
                    output += f"  ID {record.id}: {value}\n"
                else:
                    for obj in model.search([]):
                        value = self._get_relational_value(obj, self.field_name, trace_log)
                        output += f"  ID {obj.id}: {value}\n"

            if self.function_name:
                trace_log.append(f"Ejecución de función: {self.function_name}")
                output += f"\n- Resultado de la función '{self.function_name}':\n"
                
                if record:
                    func = getattr(record, self.function_name, None)
                    if callable(func):
                        result = func()
                        trace_log.append(f"Función ejecutada en registro {record.id} con resultado: {result}")

                        # Obtener la ubicación del archivo donde está definida la función
                        try:
                            func_path = inspect.getfile(func)
                            trace_log.append(f"La función se encuentra en: {func_path}")
                        except Exception as e:
                            trace_log.append(f"No se pudo obtener la ruta del archivo: {e}")

                        output += f"  ID {record.id}: {result}\n"
                    else:
                        output += f"  ID {record.id}: La función no existe o no es ejecutable.\n"
                else:
                    for obj in model.search([]):
                        func = getattr(obj, self.function_name, None)
                        if callable(func):
                            result = func()
                            trace_log.append(f"Función ejecutada en registro {obj.id} con resultado: {result}")

                            try:
                                func_path = inspect.getfile(func)
                                trace_log.append(f"La función se encuentra en: {func_path}")
                            except Exception as e:
                                trace_log.append(f"No se pudo obtener la ruta del archivo: {e}")

                            output += f"  ID {obj.id}: {result}\n"
                        else:
                            output += f"  ID {obj.id}: La función no existe o no es ejecutable.\n"

            # Agregar trazabilidad a la salida
            output += "\n--- Trazabilidad de ejecución ---\n"
            output += "\n".join(trace_log)

            self.output = output

        except Exception as e:
            _logger.error("Error ejecutando el debug: %s", e)
            self.output = f"Error: {str(e)}"

    def _get_relational_value(self, record, field_path, trace_log):
        """ Navega por relaciones y registra el proceso """
        try:
            fields = field_path.split('.')
            value = record
            trace_log.append(f"Accediendo a ruta: {field_path}")

            for field in fields:
                value = getattr(value, field, "Campo/Relación no encontrado")
                trace_log.append(f"Paso: {field} -> {value}")

                if isinstance(value, models.BaseModel):
                    value = value
                elif isinstance(value, list):
                    value = [str(v) for v in value]
                else:
                    break

            return value
        except Exception as e:
            _logger.error("Error obteniendo valor relacional: %s", e)
            trace_log.append(f"Error accediendo a '{field_path}': {str(e)}")
            return f"Error accediendo a '{field_path}': {str(e)}"