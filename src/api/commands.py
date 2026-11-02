import os

import click
from api.models import (
    db,
    User,
    LearningPath,
    Module,
    Lesson,
    Quiz,
    UserProgress,
    UserType,
)

"""
In this file, you can add as many commands as you want using the @app.cli.command decorator
Flask commands are usefull to run cronjobs or tasks outside of the API but sill in integration 
with youy database, for example: Import the price of bitcoin every night as 12am
"""


def setup_commands(app):
    """ 
    This is an example command "insert-test-users" that you can run from the command line
    by typing: $ flask insert-test-users 5
    Note: 5 is the number of users to add
    """
    @app.cli.command("insert-test-users")  # name of our command
    @click.argument("count")  # argument of out command
    def insert_test_users(count):
        print("Creating test users")
        for x in range(1, int(count) + 1):
            email = "test_user" + str(x) + "@test.com"
            user = db.session.execute(
                db.select(User).filter_by(email=email)
            ).scalar_one_or_none()
            if user is not None:
                print("User: ", email, " already exists, skipped.")
                continue
            # Antes esto asignaba `user.password` (atributo que no existe
            # en el modelo) y nunca fijaba rol ni hash: el commit reventaba
            # con IntegrityError porque password_hash es NOT NULL.
            user = User(
                email=email,
                username="Test User " + str(x),
                is_active=True,
                role=UserType.student,
            )
            user.set_password("123456")
            db.session.add(user)
            db.session.commit()
            print("User: ", user.email, " created.")

        print("All test users created")

    @app.cli.command("insert-test-data")
    def insert_test_data():
        """Populate the database with a complete, repeatable demo dataset."""
        # Los usuarios demo usan contraseñas conocidas y publicadas en el
        # repo: solo deben existir en entornos controlados (local/pruebas).
        # Por eso solo se crean si SEED_DEMO_USERS=1 está en el entorno;
        # sin la variable, la semilla puebla el contenido (rutas, módulos,
        # lecciones y quizzes) sin crear ni reactivar cuentas demo, para
        # que ningún despliegue público las deje activas por accidente.
        seed_demo_users = os.environ.get("SEED_DEMO_USERS") == "1"
        users = [
            {
                "email": "admin@academy.test",
                "username": "Admin Academy",
                "password": "Admin123!",
                "role": UserType.admin,
            },
            {
                "email": "student@academy.test",
                "username": "Demo Student",
                "password": "Student123!",
                "role": UserType.student,
            },
        ] if seed_demo_users else []

        paths = [
            {
                "title": "Fundamentos de Blockchain",
                "description": "Comprende la arquitectura descentralizada, criptografía básica y el mecanismo de consenso detrás de Bitcoin y Ethereum.",
                "image_url": "https://images.unsplash.com/photo-1639762681485-074b7f938ba0",
                "time_required": "4 horas",
                "level": "Principiante",
                "modules": [
                    {
                        "title": "Módulo 1: Conceptos esenciales",
                        "lessons": [
                            {
                                "title": "¿Qué es una blockchain?",
                                "content": """Imagina un cuaderno de cuentas que no guarda una sola persona, sino miles de personas a la vez, cada una con una copia idéntica. Cada vez que alguien anota una operación nueva, todas las copias se actualizan y nadie puede borrar ni cambiar una página antigua sin que los demás se den cuenta. Eso, en esencia, es una blockchain.

## Bloques y cadena

La información se agrupa en **bloques**: paquetes de transacciones (por ejemplo, «Ana envía 0,5 BTC a Luis»). Cada bloque guarda además una huella digital del bloque anterior, llamada **hash**. Esa huella funciona como un sello: si alguien cambia aunque sea una letra de un bloque antiguo, su hash cambia, el sello deja de coincidir con el bloque siguiente y toda la red lo detecta.

Por eso se dice que el historial es **inmutable**: no porque sea físicamente imposible escribir encima, sino porque hacerlo exige rehacer todos los bloques siguientes y convencer a la mayoría de la red, algo inviable en redes grandes.

## Nodos y descentralización

Las computadoras que guardan una copia del registro y verifican las transacciones se llaman **nodos**. No hay un servidor central: si un nodo se apaga o miente, los demás siguen funcionando con la copia correcta. Esa es la **descentralización**: el control está repartido entre muchos participantes independientes.

## Transparencia sin identidad

En una blockchain pública como Bitcoin, cualquiera puede consultar el historial completo de transacciones. Pero lo que se ve son **direcciones** (cadenas de letras y números), no nombres y apellidos. Por eso se dice que es **seudónima**: transparente en los movimientos, reservada en la identidad.

**Ejemplo:** cuando consultas un explorador de bloques y ves «la dirección X envió 0,2 BTC a la dirección Y», estás viendo esa transparencia en acción: el movimiento es público y verificable, aunque no sepas quién está detrás de cada dirección.

> **Idea clave:** una blockchain es un registro compartido por muchos nodos, donde cada bloque se enlaza al anterior con un hash; ese enlace hace que alterar el pasado sea detectable y, en la práctica, inviable.""",
                                "questions": [
                                    {
                                        "question_text": "¿Qué garantiza que un bloque ya escrito no pueda alterarse sin que la red lo note?",
                                        "option_a": "Cada bloque guarda el hash del anterior, así que alterar uno rompe toda la cadena",
                                        "option_b": "Los bloques se cifran con la clave del minero",
                                        "option_c": "Un servidor central verifica cada bloque",
                                        "correct_option": "a",
                                        "explanation": "El encadenamiento por hash hace inmutable el historial: cambiar un bloque obliga a recalcular todos los siguientes."
                                    },
                                    {
                                        "question_text": "¿Qué significa que una blockchain sea descentralizada?",
                                        "option_a": "Que está en varios servidores de la misma empresa",
                                        "option_b": "Que muchos nodos independientes guardan el registro y validan las transacciones",
                                        "option_c": "Que no tiene dueño legal registrado",
                                        "correct_option": "b",
                                        "explanation": "La descentralización está en quién valida y guarda el registro, sin una autoridad única."
                                    },
                                    {
                                        "question_text": "¿Qué es un nodo?",
                                        "option_a": "Una computadora que participa en la red guardando y validando el registro",
                                        "option_b": "Cada transacción dentro de un bloque",
                                        "option_c": "La dirección pública de una wallet",
                                        "correct_option": "a",
                                        "explanation": "Cuantos más nodos independientes, más difícil es censurar o alterar la cadena."
                                    },
                                    {
                                        "question_text": "¿Por qué se dice que una blockchain pública es transparente?",
                                        "option_a": "Porque revela la identidad real de cada usuario",
                                        "option_b": "Porque cualquiera puede leer el historial completo de transacciones",
                                        "option_c": "Porque las empresas publican sus balances en la cadena",
                                        "correct_option": "b",
                                        "explanation": "Transparencia no es identidad: el historial es público, pero las direcciones son seudónimas."
                                    }
                                ]
                            },
                            {
                                "title": "Criptografía y wallets",
                                "content": """Para usar una blockchain no abres una cuenta con usuario y contraseña: generas un par de claves. De esas claves depende todo lo demás.

## Clave pública y clave privada

- La **clave pública** sirve para recibir. De ella se deriva tu **dirección**, que es lo que compartes cuando alguien te va a pagar, como el número de cuenta de un banco.
- La **clave privada** sirve para **firmar** transacciones: es la prueba matemática de que tú autorizas mover los fondos de tu dirección. Quien tenga la clave privada, mueve los fondos. No hay excepciones ni mesa de ayuda.

La relación funciona en un solo sentido: de la clave privada se calcula la pública, pero nadie puede hacer el cálculo al revés.

## La frase semilla

Al crear una wallet, el programa te muestra una **frase semilla** (normalmente 12 o 24 palabras). Esa frase es la copia maestra de tus claves: con ella se puede regenerar tu wallet completa en cualquier dispositivo. Si la pierdes y no tienes otra copia, tus fondos quedan bloqueados para siempre; si alguien la ve, puede vaciar tu wallet. Por eso se guarda en papel, fuera de internet, y nunca se comparte.

## Wallet custodial y no custodial

- **Custodial:** un tercero (por ejemplo, un exchange) guarda tus claves. Es cómodo, pero dependes de esa empresa: si quiebra o bloquea tu cuenta, tus fondos quedan en sus manos.
- **No custodial:** tú guardas tus claves (y tu frase semilla). El control es total, y también la responsabilidad.

**Ejemplo:** dejar tus monedas en un exchange es como dejar el dinero en la caja fuerte de un negocio: práctico, pero el negocio tiene la llave. Una wallet no custodial es tu propia caja fuerte en casa: solo tú tienes la llave, y si la pierdes nadie puede abrirla por ti.

> **Idea clave:** en blockchain, la propiedad no la da un registro con tu nombre, la da el control de la clave privada. Cuida la frase semilla como lo que es: la llave maestra de tus fondos.""",
                                "questions": [
                                    {
                                        "question_text": "¿Qué permite hacer una clave privada?",
                                        "option_a": "Ocultar tu saldo a los demás usuarios",
                                        "option_b": "Firmar transacciones y demostrar que controlas los fondos de una dirección",
                                        "option_c": "Recuperar fondos enviados por error",
                                        "correct_option": "b",
                                        "explanation": "La clave privada es control. Quien la tiene, mueve los fondos."
                                    },
                                    {
                                        "question_text": "Si pierdes tu frase semilla y no tienes otra copia, ¿qué pasa con tus fondos?",
                                        "option_a": "Se pierden de forma definitiva",
                                        "option_b": "Los recuperas verificando tu identidad con el proveedor",
                                        "option_c": "Vuelven automáticamente a la dirección de origen",
                                        "correct_option": "a",
                                        "explanation": "En una wallet no custodial nadie más tiene la clave. No hay soporte que pueda recuperarla."
                                    },
                                    {
                                        "question_text": "¿Cuál es la diferencia entre una wallet custodial y una no custodial?",
                                        "option_a": "La custodial cobra comisiones y la otra es gratuita",
                                        "option_b": "En la custodial un tercero guarda tus claves; en la no custodial las guardas tú",
                                        "option_c": "La no custodial solo funciona con Bitcoin",
                                        "correct_option": "b",
                                        "explanation": "La diferencia está en quién controla las claves, y con ellas los fondos."
                                    },
                                    {
                                        "question_text": "¿Qué puedes compartir sin riesgo para recibir un pago?",
                                        "option_a": "Tu clave privada",
                                        "option_b": "Tu frase semilla",
                                        "option_c": "Tu dirección pública",
                                        "correct_option": "c",
                                        "explanation": "La dirección se deriva de la clave privada, pero el proceso no es reversible."
                                    }
                                ]
                            },
                            {
                                "title": "Transacciones paso a paso",
                                "content": """Todo lo que ocurre en una blockchain llega en forma de transacciones. Entender su recorrido es entender cómo se mueve el valor en la red.

## Qué contiene una transacción

Una transacción básica dice: «la dirección A envía X cantidad a la dirección B». Para que sea válida, el dueño de A la **firma** con su clave privada. La firma no revela la clave, pero permite a cualquiera comprobar que la autorización es auténtica.

## El recorrido completo

1. **Creación y firma:** tu wallet construye la transacción y la firmas con tu clave privada.
2. **Difusión:** la wallet la envía a la red y los nodos la propagan de unos a otros.
3. **Sala de espera (mempool):** las transacciones válidas esperan en una lista hasta que un bloque las incluye. En redes con comisión, pagar más comisión suele dar prioridad.
4. **Inclusión en un bloque:** un minero o validador incluye tu transacción en un bloque nuevo que se añade a la cadena.
5. **Confirmaciones:** cada bloque añadido encima cuenta como una confirmación más. Cuantas más confirmaciones, más costoso sería revertir tu transacción; por eso los servicios suelen esperar varias antes de dar un pago por definitivo.

## Lo que una transacción no puede hacer

Una transacción confirmada **no se puede deshacer** desde la red: no existe botón de cancelar ni devolución de cargo como en una tarjeta. Si te equivocas de dirección o de cantidad, la única vía es que el receptor decida devolver los fondos.

**Ejemplo:** envías 0,1 BTC a un amigo. Tu wallet firma, la red difunde, la transacción espera en la mempool y un minero la incluye en el siguiente bloque. Minutos después ya tiene varias confirmaciones y tu amigo puede considerarla definitiva.

> **Idea clave:** una transacción es una instrucción firmada que la red difunde, agrupa en bloques y confirma; una vez confirmada con suficiente profundidad, es irreversible.""",
                                "questions": [
                                    {
                                        "question_text": "¿Qué demuestra la firma digital de una transacción?",
                                        "option_a": "Que el emisor conoce la clave privada y autoriza el movimiento",
                                        "option_b": "Que el emisor tiene una cuenta en un exchange",
                                        "option_c": "Que la red ya cobró su comisión",
                                        "correct_option": "a",
                                        "explanation": "La firma se hace con la clave privada sin revelarla, y cualquiera puede verificarla."
                                    },
                                    {
                                        "question_text": "¿Qué es la mempool?",
                                        "option_a": "El archivo donde se guardan las claves privadas",
                                        "option_b": "La lista de espera de transacciones válidas aún no incluidas en un bloque",
                                        "option_c": "Un tipo de wallet sin conexión",
                                        "correct_option": "b",
                                        "explanation": "Las transacciones esperan en la mempool hasta que un bloque las recoge."
                                    },
                                    {
                                        "question_text": "¿Por qué los servicios esperan varias confirmaciones antes de dar un pago por definitivo?",
                                        "option_a": "Porque la firma tarda minutos en verificarse",
                                        "option_b": "Para cobrar más comisiones al usuario",
                                        "option_c": "Porque cada bloque extra hace más costoso revertir la transacción",
                                        "correct_option": "c",
                                        "explanation": "La profundidad en la cadena es lo que vuelve una transacción prácticamente irreversible."
                                    },
                                    {
                                        "question_text": "¿Se puede cancelar una transacción ya confirmada?",
                                        "option_a": "No: solo el receptor puede decidir devolver los fondos",
                                        "option_b": "Sí, desde la wallet dentro de las 24 horas",
                                        "option_c": "Sí, pagando una penalización a la red",
                                        "correct_option": "a",
                                        "explanation": "En la red no hay botón de cancelar: la irreversibilidad es parte del diseño."
                                    }
                                ]
                            }
                        ]
                    },
                    {
                        "title": "Módulo 2: Consenso",
                        "lessons": [
                            {
                                "title": "Proof of Work",
                                "content": """Miles de nodos tienen el mismo registro, pero ¿quién tiene derecho a añadir el siguiente bloque y cómo se ponen todos de acuerdo? Esa es la pregunta que responde el **mecanismo de consenso**. El primero que se usó a gran escala es Proof of Work (PoW), el de Bitcoin.

## El trabajo: buscar un hash válido

Para proponer un bloque, los **mineros** compiten resolviendo un problema de fuerza bruta: deben encontrar un número (llamado *nonce*) que, combinado con los datos del bloque, produzca un hash por debajo de un objetivo fijado por la red. No hay atajo: hay que probar millones y millones de combinaciones hasta dar con una válida.

Cuando un minero encuentra la solución, la anuncia y los demás la verifican en un instante (comprobar un hash es barato; encontrarlo es lo caro). El bloque se añade y el minero recibe la recompensa: monedas nuevas más las comisiones de las transacciones incluidas.

## Por qué el gasto asegura la red

El costo es el mecanismo de seguridad, no un desperdicio accidental. Para reescribir un bloque antiguo, un atacante tendría que rehacer ese bloque y todos los siguientes **más rápido que el resto de la red junta**, es decir, concentrar más poder de cómputo que todos los mineros honestos. Eso se conoce como **ataque del 51%**: posible en teoría, carísimo y poco rentable en redes grandes, porque el propio ataque devaluaría las monedas que el atacante intenta aprovechar.

La red además ajusta la dificultad del problema cada cierto tiempo, para que los bloques sigan saliendo a un ritmo estable aunque entren o salgan mineros.

## PoW frente a PoS

Proof of Stake (PoS), que verás en la siguiente lección, sustituye el poder de cómputo por capital bloqueado: los validadores apuestan sus propias monedas como garantía. Ambos diseños persiguen lo mismo con recursos distintos: que atacar la red salga más caro que el beneficio de atacarla.

**Ejemplo:** piensa en PoW como una lotería donde cada intento cuesta electricidad: quien más intentos compra, más opciones tiene, pero nadie puede ganar haciendo trampa sin gastar lo mismo que los demás.

> **Idea clave:** en Proof of Work, proponer bloques cuesta trabajo real y verificable; ese costo es lo que hace que mentir sea caro y decir la verdad, rentable.""",
                                "questions": [
                                    {
                                        "question_text": "¿En qué consiste el trabajo que hacen los mineros en Proof of Work?",
                                        "option_a": "Votar por el siguiente bloque según cuántas monedas tienen",
                                        "option_b": "Buscar por fuerza bruta un valor que produzca un hash bajo un objetivo dado",
                                        "option_c": "Verificar manualmente la identidad de quienes transaccionan",
                                        "correct_option": "b",
                                        "explanation": "El minero prueba millones de valores hasta dar con uno válido. Ese costo asegura la red."
                                    },
                                    {
                                        "question_text": "¿Por qué el gasto de energía es parte del diseño y no un defecto?",
                                        "option_a": "Porque hace que atacar la red sea económicamente caro",
                                        "option_b": "Porque acelera las transacciones",
                                        "option_c": "Porque permite más datos por bloque",
                                        "correct_option": "a",
                                        "explanation": "Reescribir la cadena exigiría más poder de cómputo que el resto de la red junta."
                                    },
                                    {
                                        "question_text": "¿Cuál es la diferencia central entre Proof of Work y Proof of Stake?",
                                        "option_a": "PoW usa poder de cómputo, PoS usa capital bloqueado como garantía",
                                        "option_b": "PoW es para Bitcoin y PoS solo para tokens sin valor",
                                        "option_c": "PoW no permite smart contracts y PoS sí",
                                        "correct_option": "a",
                                        "explanation": "Ambos buscan que atacar salga caro: uno lo respalda con energía y el otro con capital en riesgo."
                                    },
                                    {
                                        "question_text": "¿Qué es un ataque del 51%?",
                                        "option_a": "Cuando el 51% de los usuarios vende al mismo tiempo",
                                        "option_b": "Cuando una entidad controla más de la mitad del poder de minado y puede reescribir bloques recientes",
                                        "option_c": "Cuando el 51% de los nodos se desconecta",
                                        "correct_option": "b",
                                        "explanation": "Con mayoría de hashrate se pueden revertir transacciones recientes, aunque no robar fondos ajenos."
                                    }
                                ]
                            },
                            {
                                "title": "Proof of Stake",
                                "content": """Proof of Stake (PoS) es el otro gran mecanismo de consenso. Ethereum lo adoptó en 2022, abandonando la minería. La idea cambia la fuente de seguridad: en vez de gastar energía, los participantes bloquean su propio dinero.

## Validadores y staking

Quien quiere participar en la validación deposita una cantidad de la moneda de la red como garantía. Eso es hacer **staking**. El protocolo elige validadores para proponer y verificar bloques, con probabilidad proporcional a la cantidad bloqueada. A cambio, los validadores reciben recompensas (comisiones y, según la red, emisión nueva).

## El castigo: slashing

La garantía no es decorativa. Si un validador firma bloques contradictorios o intenta engañar a la red, el protocolo puede destruir parte de su depósito. Es el **slashing**: atacar deja de ser solo improbable; pasa a costarte tu propio capital de forma automática.

## Ventajas y debates

- **Eficiencia:** sin competencia de fuerza bruta, el consumo energético cae de forma drástica (Ethereum lo redujo en más del 99% al migrar).
- **Accesibilidad:** validar no exige hardware especializado, aunque sí capital; por eso mucha gente participa a través de servicios que agrupan fondos (*pools* de staking).
- **Debate:** los críticos señalan que quien más monedas tiene, más poder de validación acumula; los defensores responden que ese mismo capital está en riesgo si se comporta mal.

**Ejemplo:** un validador de Ethereum bloquea 32 ETH. Si valida correctamente, gana recompensas poco a poco; si intenta aprobar dos versiones de la cadena a la vez, el protocolo puede quemar parte de esos 32 ETH sin intervención humana.

> **Idea clave:** en Proof of Stake la seguridad la respalda el capital bloqueado: validar bien paga, y validar mal destruye la garantía del propio validador.""",
                                "questions": [
                                    {
                                        "question_text": "¿Qué bloquea un validador en Proof of Stake?",
                                        "option_a": "Su propio capital como garantía",
                                        "option_b": "Computadoras especializadas de minería",
                                        "option_c": "Las transacciones de otros usuarios",
                                        "correct_option": "a",
                                        "explanation": "El staking es un depósito en riesgo: es el respaldo económico de su buen comportamiento."
                                    },
                                    {
                                        "question_text": "¿Qué es el slashing?",
                                        "option_a": "Una comisión por retirar fondos del staking",
                                        "option_b": "La destrucción de parte del depósito de un validador que actúa de forma deshonesta",
                                        "option_c": "El reparto de recompensas entre validadores",
                                        "correct_option": "b",
                                        "explanation": "El protocolo castiga automáticamente al validador que firma bloques contradictorios."
                                    },
                                    {
                                        "question_text": "¿Por qué PoS consume mucha menos energía que PoW?",
                                        "option_a": "Porque los bloques son más pequeños",
                                        "option_b": "Porque funciona solo con energía renovable",
                                        "option_c": "Porque no hay competencia de fuerza bruta por resolver hashes",
                                        "correct_option": "c",
                                        "explanation": "Sin la carrera de cómputo, desaparece el gasto energético que asegura a PoW."
                                    },
                                    {
                                        "question_text": "¿Cómo se elige normalmente quién propone un bloque en PoS?",
                                        "option_a": "Con probabilidad proporcional a la cantidad en staking",
                                        "option_b": "El nodo más antiguo de la red",
                                        "option_c": "Quien tenga más transacciones históricas",
                                        "correct_option": "a",
                                        "explanation": "Más garantía bloqueada, más opciones de ser elegido (y más que perder si actúa mal)."
                                    }
                                ]
                            }
                        ]
                    }
                ]
            },
            {
                "title": "Desarrollo de Smart Contracts",
                "description": "Aprende Solidity desde cero. Crea, prueba y despliega contratos inteligentes seguros en la Ethereum Virtual Machine.",
                "image_url": "https://images.unsplash.com/photo-1639762681485-074b7f938ba0",
                "time_required": "10 horas",
                "level": "Intermedio",
                "modules": [
                    {
                        "title": "Módulo 1: Primer contrato",
                        "lessons": [
                            {
                                "title": "Estructura de Solidity",
                                "content": """Un **smart contract** es un programa que vive dentro de la blockchain: cuando se despliega, su código queda guardado en la red y cualquiera puede llamarlo, pero nadie puede cambiarlo. Solidity es el lenguaje más usado para escribirlos en Ethereum y en redes compatibles con la EVM (Ethereum Virtual Machine).

## Anatomía mínima de un contrato

```solidity
// SPDX-License-Identifier: MIT
pragma solidity ^0.8.20;

contract Contador {
    uint256 public cuenta;

    function incrementar() public {
        cuenta = cuenta + 1;
    }
}
```

- `pragma solidity ^0.8.20;` indica con qué **versiones del compilador** puede compilarse el contrato. Solidity evoluciona y un cambio de versión puede alterar el comportamiento; el pragma evita sorpresas.
- `contract Contador { ... }` agrupa todo: variables y funciones, parecido a una clase en otros lenguajes.
- `uint256 public cuenta;` es una **variable de estado**: vive en la cadena y persiste entre llamadas. Al ser `public`, el compilador genera automáticamente una función para leerla. Ojo: `private` no cifra nada; solo impide que otros contratos la lean desde código. Todo lo guardado en la cadena es visible para quien inspeccione la red.
- `incrementar()` es una **función**: al llamarla, la EVM ejecuta sus instrucciones y el cambio de estado queda registrado en un bloque.

## Funciones que reciben dinero: payable

Por defecto, una función **rechaza** el ether que intente enviarse con la llamada. Solo las funciones marcadas como `payable` pueden recibir fondos, y dentro de ellas `msg.value` contiene la cantidad recibida:

```solidity
function donar() public payable {
    // el ether queda en el contrato
}
```

## Inmutabilidad: la regla del juego

Un contrato desplegado **no se puede editar**. Si contiene un error, la corrección no es parchear el código en producción: hay que desplegar un contrato nuevo y mover a los usuarios al nuevo. Por eso en este mundo se prueba y se audita antes de desplegar, al contrario del «publica rápido y corrige después» de la web tradicional.

**Ejemplo:** el contrato `Contador` de arriba, una vez desplegado, contará para siempre con esas reglas exactas. Si mañana quisieras que `incrementar()` sumara de 2 en 2, necesitarías desplegar un `Contador` nuevo.

> **Idea clave:** un contrato Solidity define variables de estado y funciones que ejecuta la EVM; su código es inmutable tras el despliegue, así que la calidad se garantiza antes, no después.""",
                                "questions": [
                                    {
                                        "question_text": "¿Qué indica la línea pragma solidity ^0.8.20;?",
                                        "option_a": "La versión del contrato que se está escribiendo",
                                        "option_b": "Las versiones del compilador con las que el contrato puede compilarse",
                                        "option_c": "La cantidad de gas que consumirá",
                                        "correct_option": "b",
                                        "explanation": "El pragma restringe qué compilador puede usarse, para que cambios del lenguaje no rompan el contrato."
                                    },
                                    {
                                        "question_text": "¿Qué diferencia hay entre una variable public y una private?",
                                        "option_a": "La private está cifrada y nadie puede leerla",
                                        "option_b": "La public genera una función de lectura automática; la private solo restringe el acceso desde código",
                                        "option_c": "La public se guarda en la cadena y la private en el servidor",
                                        "correct_option": "b",
                                        "explanation": "Todo lo que está en la cadena es legible. private limita el acceso desde código, no la visibilidad."
                                    },
                                    {
                                        "question_text": "¿Qué significa que una función esté marcada como payable?",
                                        "option_a": "Que puede recibir ether al ser llamada",
                                        "option_b": "Que quien la llama paga una comisión extra al creador",
                                        "option_c": "Que devuelve fondos automáticamente",
                                        "correct_option": "a",
                                        "explanation": "Sin payable, una función que reciba ether revierte la transacción."
                                    },
                                    {
                                        "question_text": "¿Qué implica que un contrato desplegado sea inmutable?",
                                        "option_a": "Que su código no puede modificarse una vez en la red",
                                        "option_b": "Que nadie puede llamar a sus funciones sin permiso",
                                        "option_c": "Que su saldo queda bloqueado para siempre",
                                        "correct_option": "a",
                                        "explanation": "Por eso las auditorías importan: un error desplegado no se corrige, hay que desplegar otro contrato."
                                    }
                                ]
                            }
                        ]
                    },
                    {
                        "title": "Módulo 2: Funciones y comunicación",
                        "lessons": [
                            {
                                "title": "Funciones, visibilidad y retorno de datos",
                                "content": """Si la lección anterior fue la anatomía de un contrato, esta es su comportamiento: cómo recibe órdenes, quién puede dárselas y cómo responde.

## Visibilidad: quién puede llamar a quién

Cada función declara quién puede llamarla:

- `public`: cualquiera, desde fuera del contrato y también desde dentro.
- `external`: solo desde fuera (otros contratos o transacciones). Es la opción eficiente para funciones que solo se usan desde fuera.
- `internal`: solo el propio contrato y los que hereden de él.
- `private`: solo el propio contrato.

Las variables de estado usan las mismas etiquetas (menos `external`). Recuerda: la visibilidad controla el acceso **desde código**; los datos en la cadena siguen siendo legibles por cualquiera que inspeccione la red.

## Funciones que leen y funciones que escriben

- `view`: la función **lee** el estado pero no lo modifica. Llamarla desde fuera no cuesta gas, porque no cambia nada en la cadena.
- `pure`: ni lee ni escribe el estado; solo calcula con los datos que recibe.
- Sin etiqueta: la función **escribe** el estado. Cada llamada es una transacción que cuesta gas y queda registrada en un bloque.

```solidity
contract Ejemplo {
    uint256 private total;

    function sumar(uint256 valor) public {
        total = total + valor;      // escribe: cuesta gas
    }

    function verTotal() public view returns (uint256) {
        return total;               // lee: llamada gratuita
    }

    function doble(uint256 n) public pure returns (uint256) {
        return n * 2;               // calcula: no toca el estado
    }
}
```

## Parámetros y retornos

`returns (uint256)` declara qué devuelve la función. En Solidity las funciones pueden devolver varios valores a la vez, algo muy usado para consultar datos compuestos.

**Ejemplo:** un contrato de votaciones podría tener `votar(uint256 opcion)` como función pública que escribe, y `resultados() public view returns (uint256, uint256)` para consultar el conteo sin coste.

> **Idea clave:** la visibilidad decide quién puede llamar, y `view`/`pure` separan las consultas gratuitas de las escrituras que cuestan gas y cambian el estado.""",
                                "questions": [
                                    {
                                        "question_text": "¿Qué visibilidad permite llamar a una función solo desde fuera del contrato?",
                                        "option_a": "external",
                                        "option_b": "private",
                                        "option_c": "internal",
                                        "correct_option": "a",
                                        "explanation": "external está pensada para funciones que solo se invocan con transacciones o desde otros contratos."
                                    },
                                    {
                                        "question_text": "¿Por qué llamar a una función view desde fuera no cuesta gas?",
                                        "option_a": "Porque es más corta que las demás",
                                        "option_b": "Porque no modifica el estado de la cadena",
                                        "option_c": "Porque se ejecuta en el servidor del usuario",
                                        "correct_option": "b",
                                        "explanation": "Si no hay cambio de estado, no hay nada que registrar en un bloque."
                                    },
                                    {
                                        "question_text": "¿Qué hace una función pure?",
                                        "option_a": "Borra el estado del contrato",
                                        "option_b": "Recibe ether y lo guarda",
                                        "option_c": "Calcula con los parámetros sin leer ni escribir el estado",
                                        "correct_option": "c",
                                        "explanation": "pure es una calculadora aislada: entra un valor, sale un resultado."
                                    },
                                    {
                                        "question_text": "¿Una variable private está cifrada en la cadena?",
                                        "option_a": "No: solo restringe el acceso desde código; los datos en cadena son legibles",
                                        "option_b": "Sí, con la clave privada del dueño",
                                        "option_c": "Sí, siempre que use uint256",
                                        "correct_option": "a",
                                        "explanation": "La visibilidad regula el código, no la transparencia de la red."
                                    }
                                ]
                            },
                            {
                                "title": "Eventos y manejo de errores",
                                "content": """Un contrato necesita dos cosas que el estado por sí solo no da: avisar al exterior de lo que ocurrió y rechazar operaciones inválidas. Para eso están los **eventos** y las comprobaciones con `require` y `revert`.

## Eventos: el registro barato que sí se puede consultar

Cuando una función cambia el estado, puede **emitir un evento**. Los eventos quedan guardados en el recibo de la transacción, fuera del estado del contrato: por eso son mucho más baratos que guardar variables, y por eso las aplicaciones los usan para enterarse de lo que pasa sin releer todo el contrato.

```solidity
event Deposito(address indexed quien, uint256 cantidad);

function depositar() public payable {
    emit Deposito(msg.sender, msg.value);
}
```

`msg.sender` es la dirección que llama a la función y `msg.value` la cantidad de ether recibida. El parámetro `indexed` permite buscar eventos filtrando por ese valor (por ejemplo, todos los depósitos de una dirección).

## Errores: require y revert

`require(condición, "mensaje")` comprueba una condición antes de seguir: si no se cumple, la transacción **revierte** — se deshacen todos los cambios de esa llamada y el usuario recibe el mensaje de error (el gas ya consumido no se devuelve).

```solidity
function retirar(uint256 cantidad) public {
    require(cantidad > 0, "La cantidad debe ser mayor que cero");
    // ...resto de la lógica
}
```

Revertir protege al contrato de estados imposibles: saldos negativos, operaciones de quien no tiene permiso o cantidades sin sentido nunca llegan a escribirse.

**Ejemplo:** en una tienda escrita como contrato, cada compra emitiría un evento `Compra(comprador, producto, precio)`. La web de la tienda escucha esos eventos y actualiza el inventario en pantalla sin consultar el estado completo tras cada venta.

> **Idea clave:** los eventos comunican hacia fuera de forma barata y consultable; `require`/`revert` impiden que una operación inválida deje huella en el estado.""",
                                "questions": [
                                    {
                                        "question_text": "¿Para qué sirve emitir un evento en un contrato?",
                                        "option_a": "Para registrar lo ocurrido de forma barata y consultable desde fuera",
                                        "option_b": "Para cifrar el estado del contrato",
                                        "option_c": "Para que las funciones no paguen gas nunca",
                                        "correct_option": "a",
                                        "explanation": "Los eventos viven en el recibo de la transacción: avisar sale mucho más barato que guardar variables."
                                    },
                                    {
                                        "question_text": "¿Qué pasa cuando un require no se cumple?",
                                        "option_a": "El contrato se borra de la red",
                                        "option_b": "La transacción revierte y se deshacen sus cambios",
                                        "option_c": "Se cobra doble gas y la operación continúa",
                                        "correct_option": "b",
                                        "explanation": "Revertir garantiza que una operación inválida nunca llega a escribirse en el estado."
                                    },
                                    {
                                        "question_text": "¿Qué es msg.sender?",
                                        "option_a": "El minero del bloque actual",
                                        "option_b": "Siempre el creador del contrato",
                                        "option_c": "La dirección que está llamando a la función",
                                        "correct_option": "c",
                                        "explanation": "msg.sender cambia con cada llamada: es quien firma la transacción en curso."
                                    },
                                    {
                                        "question_text": "¿Por qué los eventos son más baratos que guardar variables de estado?",
                                        "option_a": "Porque se guardan en el recibo de la transacción, no en el estado",
                                        "option_b": "Porque se comprimen automáticamente",
                                        "option_c": "Porque no se guardan en la red",
                                        "correct_option": "a",
                                        "explanation": "El estado es lo más caro de la EVM; el recibo es un registro pensado para consultar, no para ejecutar."
                                    }
                                ]
                            }
                        ]
                    },
                    {
                        "title": "Módulo 3: Seguridad esencial",
                        "lessons": [
                            {
                                "title": "Buenas prácticas de seguridad en contratos",
                                "content": """Un contrato desplegado maneja dinero real y no se puede corregir. La mayoría de los grandes robos en DeFi no rompieron la criptografía: explotaron errores de lógica que se repiten. Conocer los patrones básicos es la diferencia entre un contrato de juguete y uno defendible.

## El patrón checks-effects-interactions

El ataque clásico es la **reentrada**: un contrato malicioso recibe fondos y, antes de que tu contrato actualice el saldo, vuelve a llamar a la función de retiro y cobra dos veces. El robo de The DAO en 2016 funcionó así.

La defensa estándar ordena cada función en tres pasos:

1. **Checks:** comprobar condiciones (saldos, permisos) con `require`.
2. **Effects:** actualizar el estado (descontar el saldo) **antes** de enviar nada.
3. **Interactions:** al final, interactuar con direcciones externas (enviar fondos).

Si el saldo ya se descontó antes de enviar, una segunda llamada encuentra el saldo en cero y revierte.

```solidity
function retirar(uint256 cantidad) public {
    require(saldos[msg.sender] >= cantidad, "Saldo insuficiente"); // checks
    saldos[msg.sender] -= cantidad;                                  // effects
    (bool ok, ) = msg.sender.call{value: cantidad}("");              // interactions
    require(ok, "La transferencia fallo");
}
```

## Otras reglas que no se negocian

- **Control de acceso:** las funciones sensibles comprueban quién llama (por ejemplo, que solo el propietario pueda pausar el contrato). Un `public` descuidado en la función equivocada deja la puerta abierta.
- **Que cada quien retire lo suyo:** en vez de empujar pagos a muchas direcciones (una sola problemática puede bloquear a todas), deja que cada usuario retire sus fondos cuando quiera.
- **Prueba antes de desplegar:** redes de prueba, tests automáticos y, si hay dinero real de por medio, auditoría externa. En contratos, probar no es un paso más: es el producto.

**Ejemplo:** el contrato de retiros de arriba sigue pagando igual de bien que una versión ingenua, pero su orden interno hace que un ataque de reentrada se encuentre la puerta ya cerrada.

> **Idea clave:** en contratos que mueven dinero, el orden importa: primero comprueba, después actualiza el estado y solo al final interactúa con el exterior. Y todo se prueba antes de desplegar, porque después no hay parche.""",
                                "questions": [
                                    {
                                        "question_text": "¿Qué es un ataque de reentrada?",
                                        "option_a": "Volver a llamar a una función antes de que actualice el estado, para cobrar dos veces",
                                        "option_b": "Entrar dos veces con la misma contraseña",
                                        "option_c": "Desplegar el mismo contrato dos veces",
                                        "correct_option": "a",
                                        "explanation": "El atacante explota la ventana entre enviar los fondos y actualizar el saldo."
                                    },
                                    {
                                        "question_text": "¿En qué orden actúa el patrón checks-effects-interactions?",
                                        "option_a": "Enviar fondos primero y comprobar después",
                                        "option_b": "Comprobar, actualizar el estado e interactuar al final",
                                        "option_c": "Interactuar, comprobar y actualizar",
                                        "correct_option": "b",
                                        "explanation": "Con el estado ya actualizado, una llamada repetida encuentra el saldo correcto y revierte."
                                    },
                                    {
                                        "question_text": "¿Por qué es tan grave un error en un contrato ya desplegado?",
                                        "option_a": "Porque la red borra el contrato con errores",
                                        "option_b": "Porque duplica el saldo de los usuarios",
                                        "option_c": "Porque el código es inmutable: la corrección exige desplegar un contrato nuevo",
                                        "correct_option": "c",
                                        "explanation": "No hay parche en producción; por eso la calidad se asegura antes del despliegue."
                                    },
                                    {
                                        "question_text": "¿Qué reduce el riesgo antes del despliegue?",
                                        "option_a": "Probar en redes de prueba, escribir tests y auditar si hay dinero real",
                                        "option_b": "Desplegar en horas de poca actividad",
                                        "option_c": "Usar nombres de variables cortos",
                                        "correct_option": "a",
                                        "explanation": "En contratos, la verificación previa es la principal línea de defensa."
                                    }
                                ]
                            }
                        ]
                    }
                ]
            },
        ]

        created_users = 0
        created_paths = 0
        created_modules = 0
        created_lessons = 0
        created_quizzes = 0
        created_progress = 0

        try:
            user_by_email = {}
            for user_data in users:
                user = db.session.execute(
                    db.select(User).filter_by(email=user_data["email"])
                ).scalar_one_or_none()
                if user is None:
                    user = User(
                        email=user_data["email"],
                        username=user_data["username"],
                        is_active=True,
                        role=user_data["role"],
                    )
                    user.set_password(user_data["password"])
                    db.session.add(user)
                    created_users += 1
                user_by_email[user_data["email"]] = user

            db.session.flush()
            # Sin usuarios demo no hay estudiante al que sembrar progreso.
            student = user_by_email.get("student@academy.test")

            for path_data in paths:
                path = db.session.execute(
                    db.select(LearningPath).filter_by(title=path_data["title"])
                ).scalar_one_or_none()
                if path is None:
                    path = LearningPath(title=path_data["title"])
                    db.session.add(path)
                    created_paths += 1

                path.description = path_data["description"]
                path.image_url = path_data["image_url"]
                path.time_required = path_data["time_required"]
                path.level = path_data["level"]
                db.session.flush()

                for module_data in path_data["modules"]:
                    module = db.session.execute(
                        db.select(Module).filter_by(
                            title=module_data["title"], learning_path_id=path.id
                        )
                    ).scalar_one_or_none()
                    if module is None:
                        module = Module(
                            title=module_data["title"],
                            level=path.level,
                            learning_path=path,
                        )
                        db.session.add(module)
                        created_modules += 1
                    else:
                        module.level = path.level
                    db.session.flush()

                    for order_number, lesson_data in enumerate(
                        module_data["lessons"], start=1
                    ):
                        lesson = db.session.execute(
                            db.select(Lesson).filter_by(
                                title=lesson_data["title"], module_id=module.id
                            )
                        ).scalar_one_or_none()
                        if lesson is None:
                            lesson = Lesson(
                                title=lesson_data["title"],
                                content=lesson_data["content"],
                                order_number=order_number,
                                module=module,
                            )
                            db.session.add(lesson)
                            created_lessons += 1
                        else:
                            lesson.content = lesson_data["content"]
                            lesson.order_number = order_number
                        db.session.flush()

                        quiz = db.session.execute(
                            db.select(Quiz).filter_by(lesson_id=lesson.id)
                        ).scalar_one_or_none()
                        if quiz is None:
                            db.session.add(
                                Quiz(
                                    lesson=lesson,
                                    questions_data=lesson_data["questions"],
                                )
                            )
                            created_quizzes += 1
                        else:
                            quiz.questions_data = lesson_data["questions"]

                        if student is not None:
                            progress = db.session.execute(
                                db.select(UserProgress).filter_by(
                                    user_id=student.id, lesson_id=lesson.id
                                )
                            ).scalar_one_or_none()
                            if progress is None:
                                db.session.add(
                                    UserProgress(
                                        user=student,
                                        lesson=lesson,
                                        is_completed=False,
                                    )
                                )
                                created_progress += 1

            db.session.commit()
        except Exception:
            db.session.rollback()
            raise

        print(
            "Seed completado: "
            f"{created_users} usuarios, {created_paths} rutas, "
            f"{created_modules} módulos, {created_lessons} lecciones, "
            f"{created_quizzes} quizzes y {created_progress} progresos creados."
        )
        if seed_demo_users:
            print("Usuario demo: student@academy.test / Student123!")
            print("Administrador demo: admin@academy.test / Admin123!")
        else:
            print(
                "Usuarios demo omitidos: define SEED_DEMO_USERS=1 para "
                "crearlos en entornos controlados (local/pruebas)."
            )
