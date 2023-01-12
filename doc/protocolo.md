PREAT (Protocol for remote execution of automated tests)

-----
**Tabla de Contenido**

[Formato de las tramas](#formato-de-las-tramas)
[Campo Parámetros](#campo-parámetros-parametros)
[Clase STATUS](#clase-status)
[Clase BLOB](#clase-blob)
[Clase TEST](#clase-test)
[Ejemplos de Uso](#ejemplos-de-uso)
[Pruebas efectuadas](#pruebas-efectuadas)

## Formato de las tramas

Las tramas son de longitud variable, con un mínimo de 40 bits (5 bytes) y un máximo 512 bits (64 bytes), pero siempre con una cantidad de bits múltiplo de 8. Los datos se acomodan en la trama y en memoria siguiendo el esquema big-endiand, es decir que el byte más significativo se transmite primero y, por lo tanto, se ubica en la dirección mas baja de memoria en el buffer de transmisión y/o recepción.

El formato general de las tramas es el siguiente:

| Longitud | Método  | Cantidad | Parámetros    | CRC     |
|:--------:|:-------:|:--------:|:-------------:|:-------:|
| 8        | 12      | 4        |  0 a 472      | 16      |

- **Longitud:** Indica la longitud total de la trama en bytes, incluido el propio campo de longitud. Solo son válidos los valores del 5 al 64.

- **Clase:** Indica la clase a la que pertenece el método que ejecutará la acción requerida por la trama.

- **Método:** Indica el método dentro de la clase que ejecutará la acción requerida por la trama.

- **Cantidad:** Indica la cantidad de parámetros que requiere el método que se ejecutará para completar la acción requerida por la trama.

- **Parámetros:** Define los tipos de datos y valores de los parámetros con los que se ejecutará el método para completar la acción requerida por la trama. El formato se detalla en la sección *[Campo Parámetros](#parametros)*

- **CRC:** Control de redundancia cíclica para detección de errores. Se calcula sobre el total de la trama incluido el campo de longitud. Se utiliza el polinomio 0xD175 (0x1A2EB = x^16^ + x^15^ + x^13^ + x^9^ + x^7^ + x^6^ + x^5^ + x^3^ + x + 1). Para el cálculo del CRC se inicializa el valor del registro en 0x0000 y no se realiza reflexión de los bytes ni a la entrada o a la salida, ni una operación XOR adicional al final sobre el valor calculado. El CRC puede calcularse con el siguiente comando python

```
pycrc --width=16 --poly=0xD175 --reflect-in=false --xor-in=0x00 --reflect-out=false --xor-out=0x00 --check-hexstring=""
```

## Campo Parámetros {#parametros}

El campo parámetros está formado por una repetición de la siguiente estructura

| Tipo | Valor    | Valor  |
|:----:|:--------:|:------:|
| 8    | 8 a 464  | 0 a 32 |

- **Tipo:** Cuando el bit más significativo de este campo es cero entonces el valor debe ser interpretado como dos nibbles independientes donde el nibble más significativo indica el tipo de datos del primer campo de parámetros y el nibble menos significativo el del segundo campo. Si el bit más significativo de este campo es uno entonces la secuencia está formada por un solo valor y los siete bits restantes indican la longitud, en bytes, de este campo.

- **Valor:** Valor del parámetro.

La siguiente tabla tiene la codificación utilizada para

| Valor | Tipo de datos  | Longitud |
|:-----:|:---------------|:---------|
| 0x0   | No existe      | 0 byte   |
| 0x1   | Entero         | 1 byte   |
| 0x2   | Entero         | 2 bytes  |
| 0x3   | Entero         | 4 bytes  |
| 0x7   | Blob           | 1 byte   |
| 0x81  | Bytes          | 1 byte   |
| ...   | ...            | ...      |
| 0xBA  | Bytes          | 58 bytes |

---

## Clase STATUS

La placa de periféricos responde a cada comando enviado por el supervisor con una de las dos funciones de esta clase.

#### `STATUS.Completed() (0x000)`

El último comando enviado por el supervisor fue ejecutado sin errores

#### `STATUS.Error(uint8:codigo) (0x001)`

Se produjo un error al ejecutar el último comando enviado por el supervisor y el parámetro *codigo*, contiene más información acerca del error. En la siguiente tabla se detalla cada uno de los códigos de error asignados.

| Error | Nombre     | Descripción del error                                                           |
|:-----:|:---------- |:--------------------------------------------------------------------------------|
|  0x01 | CRC        | La trama recibida fue alterada y no verifica el control CRC                     |
|  0x02 | METHOD     | El campo función de la trama recibida no corresponde a ningún método definido   |
|  0x03 | PARAMETERS | Los parámetros recibidos no corresponden a los esperados por el método invocado |
|  0x04 | TOO_EARLY  | Las condiciones de la prueba se verificaron antes del tiempo mínimo de espera   |
|  0x05 | TIMEOUT    | Se superó el tiempo máximo de espera para las condiciones de la prueba          |
|  0x06 | UNDEFINED  | El blob al que se hace referencia no fue previamente definido                   |
|  0x07 | REDEFINED  | El blob que se quiere crear ya fue previamente definido                         |
|  0xFF | GENERIC    | Error particular que no corresponde con ninguno de los códigos definidos        |


## Clase BLOB

Es espacio total disponible en la trama para almacenar los parámetros de la llamada a un método es de 54, por esta razón cuando se requieren bloques de datos de mayor tamaño deben ser previamente definidos y cargados para ser referenciados en la llamada al método.

#### `BLOB.Create(uint8:id, uint32:size) (0x002)`

Este método crea un nuevo bloque de datos de tamaño *size*, el cual se podrá referenciar utilizando el identificador *id*. El nuevo bloque se rellena con el valor 0x00:NULL. Si ya existe un bloque previamente definido con el mismo identificador *id* entonces la operación devuelve un error 0x05:REDEFINED.


#### `BLOB.Update(uint8:id, uint16:offset, bytes:data) (0x003)`

Este método actualiza un fragmento del contenido del bloque de datos con el identificador *id*, escribiendo los bytes de *data* a partir del desplazamiento *offset* medido en bytes desde el inicio del bloque. Si el bloque de datos no fue previamente definido entonces la operación devuelve un error 0x04:UNDEFINED.

#### `BLOB.Destroy(uint8:id) (0x004)`

Este método destruye un bloque de datos binario previamente definido con el identificador *id*. Si el bloque de datos no fue previamente definido entonces la operación devuelve un error 0x04:UNDEFINED.

## Clase TEST

Al ejecutar una prueba la placa de periféricos debe poder verificar las respuestas recibidas en las entradas como resultado de una acción que la prueba ejecuta sobre las salidas.

#### `TEST.Assert(uint32:min, uint32:max, uint8:conditions, uint8:operator) (0x005)`

Define una prueba formada por *conditions* verificaciones sobre entradas, las cuales se combinan utilizando el operador lógico *operator*. Las entradas deben cumplir las espectativas antes del tiempo máximo *max* pero después de un tiempo mínimo *min*

## Clase GPIO

#### `GPIO.Set(uint8:output) (0x010)`

Fija el estado lógico de la salida *output* en el valor lógico 1:VERDADERO.

#### `GPIO.Clear(uint8:output) (0x011)`

Fija el estado lógico de la salida *output* en el valor loógico 0:FALSO.

#### `GPIO.Toggle(uint8:output) (0x0012)`

Cambia el estado lógico actual de la salida *output* por el valor complementario.

#### `GPIO.HasRissing(uint8:input) (0x013)`

Verifica que en la entrada *input* se produzca una transición del estado 0:FALSO al 1:VERDADERO.

#### `GPIO.HasFalling(uint8:input) (0x013)`

Verifica que en la entrada *input* se produzca una transición del estado 1:VERDADERO al 0:FALSO.

#### `GPIO.IsSet(uint8:input) (0x014)`

Verifica que en la entrada *input* se encuentre en el valor lógico 1:VERDADERO.

#### `GPIO.IsSet(uint8:input) (0x015)`

Verifica que en la entrada *input* se encuentre en el valor lógico 0:FALSO.

## Ejemplos de Uso

Se desea probar que un sistema responde a la activación de una entrada digital activando una salida digital entre 100ms y 250ms después de cambio en la entrada.

`GPIO.Set(0)`

`TEST.Assert(100, 250, 1, AND)`
`GPIO.HasRissing(2)`
`GPIO.Set(1)`

## Pruebas Efectuadas


#### Activación de salidas digitales

1. **Comandos implementados**

    | Mnemonico          | Longitud | Método   | Cantidad | Tipo     | Valor |
    |:-------------------|:--------:|:--------:|:--------:|:--------:|:-----:|
    | STATUS.Completed() | 0x05     | 0x000    | 0x0      | N/A      | N/A   |
    | STATUS.Error(x)    | 0x07     | 0x001    | 0x1      | 0x1 0x0  |   x   |
    | GPIO.Set(x)        | 0x07     | 0x010    | 0x1      | 0x1 0x0  |   x   |
    | GPIO.Clear(x)      | 0x07     | 0x011    | 0x1      | 0x1 0x0  |   x   |

2. **Comandos usados en las pruebas**

    | Mnemonico                | Longitud | Método y Cantidad | Tipo     | Valor | CRC       |
    |:-------------------------|:--------:|:-----------------:|:--------:|:-----:|:---------:|
    | STATUS.Completed()       | 0x05     | 0x00 0x00         |          |       | 0xA1 0xB5 |
    | STATUS.Error(CRC)        | 0x07     | 0x00 0x11         | 0x10     | 0x01  | 0xCC 0x08 |
    | STATUS.Error(METHOD)     | 0x07     | 0x00 0x11         | 0x10     | 0x02  | 0x6E 0xE2 |
    | STATUS.Error(PARAMETERS) | 0x07     | 0x00 0x11         | 0x10     | 0x03  | 0xBF 0x97 |
    | GPIO.Set(1)              | 0x07     | 0x01 0x01         | 0x10     | 0x01  | 0xB5 0xA3 |
    | GPIO.Clear(2)            | 0x07     | 0x01 0x11         | 0x10     | 0x02  | 0xD3 0x15 |
