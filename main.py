from flask import Flask, render_template, redirect, flash, url_for, session, request
from forms import Register_form, Login_form, Añadir_medicamento, Contacto, Ver_consultas, Vaciar_tubo, Deshabilitar_tubo, Habilitar_tubo
import sqlite3
import os
from datetime import timedelta, datetime, date
import smtplib

#Inicio la app
app = Flask(__name__)  # nombre del modulo
app.debug = True
SECRET_KEY = os.urandom(32)
app.config['SECRET_KEY'] = SECRET_KEY
app.permanent_session_lifetime = timedelta(minutes=30)


##################################FUNCIONES######################################
##################################FUNCIONES######################################

def logueado():
    if "padim" in session:
        return True
    else:
        return False

def validar_medicamento(nombre, id):
    conn = sqlite3.connect("PADIM.db")
    nombres_medicamentos_cursor = conn.execute(f"SELECT nombre FROM padim_tubos WHERE id_padim = {id}")
    for nombre in nombres_medicamentos_cursor.fetchall():
        if nombre[0] == nombre:
            conn.close()
            return False
    conn.close()
    return True

def enviar_mail(nombre,apellido,mail,telefono):
    server = smtplib.SMTP('64.233.184.108')
    server.starttls()
    server.login('proyecto6to2021@gmail.com', '2021fernando')
    header = f'Recivimos tu consulta {nombre}'
    body = f'Hola {nombre} {apellido}, te queremos avisar de que tu consulta nos llego exitosamente, en las proximas 24hs te vamos a contactar via mail, o via el telefono que indicaste en el formulario ({telefono})'
    msg = f"Subject: {header}\n\n{body}"
    server.sendmail('proyecto6to2021@gmail.com', mail, msg)
    server.close()

def enviar_respuesta(mail, mensaje):
    server = smtplib.SMTP('64.233.184.108')
    server.starttls()
    server.login('proyecto6to2021@gmail.com', '2021fernando')
    header = f'Respuesta a tu consulta'
    msg = f"Subject: {header}\n\n{mensaje}"
    server.sendmail('proyecto6to2021@gmail.com', mail, msg)
    server.close()

##################################FUNCIONES######################################
##################################FUNCIONES######################################

#Enruto para home
@app.route("/", methods=['POST', 'GET'])
def home():
    if logueado():
        id_padim = session["padim"]
        return render_template("Home.html", padim=id_padim)
    else:
        return render_template("Home.html")


@app.route("/comprar")
def comprar():
    if logueado():
        id_padim = session["padim"]
        return render_template("Comprar.html", padim=id_padim)
    else:
        return render_template("Comprar.html")


#enruto para añadir/modificar medicamento
@app.route("/añadirmedicamento/<tubo>", methods=['POST', 'GET'])
def añadir_medicamento(tubo):
    if logueado():
        id_padim = session["padim"]
    else:
        flash("Por favor, inicia secion para añadir medicamentos", "info")
        return redirect(url_for('login'))
    añadir_form = Añadir_medicamento()
    vaciar_form = Vaciar_tubo()
    deshabilitar_form = Deshabilitar_tubo()
    habilitar_form = Habilitar_tubo()
    conn = sqlite3.connect('PADIM.db')

    if añadir_form.submit_medicamento.data and añadir_form.validate():
        if validar_medicamento(añadir_form.nombre.data, id_padim):
            conn = sqlite3.connect('PADIM.db')
            dias_f = añadir_form.dia.data
            dias = ""
            for dia in dias_f:
                dias = dias + dia + ','
            dias = dias[:-1]
            if añadir_form.toma_libre.data:
                toma_libre = 1
            else:
                toma_libre = 0

            horario = str(añadir_form.horario.data)

            sql_update_med = f"UPDATE padim_tubos SET nombre = '{añadir_form.nombre.data}',dias = '{dias}',horario = '{horario[0:5]}', repeticion = '{añadir_form.repeticion.data}', toma_libre = {toma_libre}, mensaje = '{añadir_form.mensaje.data}', cantidad_dispensar = '{añadir_form.cantidad.data}' WHERE id_padim = {id_padim} AND id_tubo = {int(tubo)}"

            conn.execute(sql_update_med)
            conn.commit()
            conn.close()
            flash("Se guardo el medicamento correctamente", "success")
            return redirect(url_for('ver_padim'))

        else:
            flash("Ya tenes un medicamento con ese nombre", "danger")
            return redirect(url_for('añadir_medicamento'))
    elif vaciar_form.submit1.data and vaciar_form.validate():
        conn.execute(f"UPDATE padim_tubos SET nombre = NULL, cantidad_dispensar = NULL, horario = NULL, dias = NULL, repeticion = NULL, toma_libre = NULL, mensaje = NULL, cantidad_disponible = NULL, carga = 0, vaciar = 1 WHERE id_padim = {id_padim} AND id_tubo = {tubo}")
        flash("Se vacio el tubo correctamente", "info")
        conn.commit()
        return redirect(url_for('ver_padim'))

    elif deshabilitar_form.submit2.data and deshabilitar_form.validate():
        conn.execute(f"UPDATE padim_tubos SET hab_dispensar = 0 WHERE id_padim = {id_padim} AND id_tubo = {tubo}")
        flash("Se deshabilito el tubo correctamente", "info")
        conn.commit()
        return redirect(url_for('ver_padim'))

    elif habilitar_form.submit3.data and habilitar_form.validate():
        conn.execute(f"UPDATE padim_tubos SET hab_dispensar = 1 WHERE id_padim = {id_padim} AND id_tubo = {tubo}")
        flash("Se habilito el tubo correctamente", "info")
        conn.commit()
        return redirect(url_for('ver_padim'))

    consulta_medicamento = conn.execute(f"SELECT * FROM padim_tubos WHERE id_padim = { id_padim } AND id_tubo = { tubo }")
    medicamento_tubo = consulta_medicamento.fetchall()
    medicamento = medicamento_tubo[0]
    if medicamento[2]:
        añadir_form.repeticion.default = medicamento[6]
        dias_f = str(medicamento[5])
        dias_f.replace(",","")
        dias = []
        for letra in dias_f:
            dias.append(letra)
        añadir_form.dia.default = dias
        añadir_form.process()
    return render_template("AñadirMedicamentos.html",padim=id_padim ,añadir_form=añadir_form, vaciar_form=vaciar_form, habilitar_form=habilitar_form, deshabilitar_form=deshabilitar_form, title="añadir medicamento", medicamento = medicamento_tubo[0])

#enruto para ver padim
@app.route("/ver-padim/", methods=['POST', 'GET'], defaults={'carga_tubo': 0})
@app.route("/ver-padim/<carga_tubo>", methods=['POST', 'GET'])
def ver_padim(carga_tubo):
    if logueado():
        id_padim = session["padim"]

    else:
        flash("Por favor, inicia secion para ver tu P.A.D.I.M", "info")
        return redirect(url_for('login'))

    conn = sqlite3.connect('PADIM.db')
    consulta_medicamentos = conn.execute(f"SELECT * FROM 'padim_tubos' WHERE id_padim = {id_padim}")
    medicamentos = consulta_medicamentos.fetchall()

    consulta_tomas = conn.execute(f"SELECT * FROM tomas WHERE id_padim = {id_padim} ORDER BY toma_id DESC LIMIT 3")
    consulta_dispensacion = conn.execute(f"SELECT * FROM dispensacion WHERE id_padim = {id_padim} ORDER BY id_dispensacion DESC LIMIT 3")
    consulta_conexion = conn.execute(f"SELECT * FROM conexion WHERE id_padim = {id_padim} ORDER BY conexion_id DESC LIMIT 3")
    tomas = consulta_tomas.fetchall()
    print(tomas)
    dispensacion = consulta_dispensacion.fetchall()
    print(dispensacion)
    conexion = consulta_conexion.fetchall()
    print(conexion)

    ev_conexion = []
    conectado = 0
    for ev_conn in conexion:
        horario = ev_conn[2]
        print("horario = ",horario)
        hora = int(horario[0:2])
        print("hora", hora)
        now = datetime.now()
        hora_act = int(now.strftime("%H"))
        print("hora actual: ",hora_act)
        if hora == hora_act:
            minutos = int(horario[3:5])
            print("minutos: ", minutos)
            minutos_act = int(now.strftime("%M"))
            print("minutos actuales: ", minutos_act)
            for i in range(11):
                if minutos == minutos_act - i:
                    conectado = 1
            print(conectado)
    ev_conexion.append(conectado)
    if conectado == 0:
        if conexion:
            ev_conexion.append(ev_conn[1])
            ev_conexion.append(horario)
        else:
            dia = datetime.today().strftime('%A')
            ev_conexion.append(dia[0:3])
            hora = datetime.now().strftime('%H:%M')
            ev_conexion.append(hora)
    print("evento conexion: ", ev_conexion)

    #VER CUANDO SE MUESTRA EL MENSAJE DE ERROR
    if 0 < int(carga_tubo) < 7:
        add_carga = conn.execute(f"UPDATE padim_tubos SET carga = 1 WHERE id_padim = {id_padim} AND id_tubo = {int(carga_tubo)}")
        conn.commit()
        nombre_carga = conn.execute(f"SELECT nombre FROM padim_tubos WHERE id_padim = {id_padim} AND id_tubo = {int(carga_tubo)}")
        nombre_carga = nombre_carga.fetchall()
        nombre = nombre_carga[0]
        flash(f"Se esta cargando {nombre[0]}", "info")
    elif carga_tubo:
        flash("ERROR tubo incorrecto", "danger")

    carga_tubo = 0
    cargas_con = conn.execute(f"SELECT carga FROM padim_tubos WHERE id_padim = {id_padim}")
    cargas = cargas_con.fetchall()
    for carga in cargas:
        if carga[0] == 1:
            carga_tubo = 1
    conn.close()
    return render_template("VerMedicamentos.html", title="ver padim", carga_tubo=carga_tubo, padim=id_padim, medicamentos=medicamentos, ev_tomas = tomas, ev_dispenser = dispensacion, ev_conexion = ev_conexion)

#Enruto para pagina de contacto
@app.route("/contacto", methods=['POST', 'GET'])
def contacto():
    if logueado():
        id_padim = session["padim"]
    else:
        id_padim = None

    if id_padim != 'empleado':
        form = Contacto()
        if form.validate_on_submit():
            enviar_mail(form.nombre.data, form.apellido.data, form.mail.data, form.telefono.data)
            conn = sqlite3.connect('PADIM.db')

            hoy = date.today()
            fecha = hoy.strftime("%d/%m/%Y")
            add_consulta = f"INSERT INTO consultas (nombre, apellido, telefono, mail, mensaje, fecha)\
                            VALUES ('{form.nombre.data}', '{form.apellido.data}', {form.telefono.data}, '{form.mail.data}', '{form.mensaje.data}', '{fecha}')"
            if id_padim:
                add_consulta = f"INSERT INTO consultas (nombre, apellido, telefono, mail, mensaje, usuario, fecha)\
                                VALUES ('{form.nombre.data}', '{form.apellido.data}', {form.telefono.data}, '{form.mail.data}', '{form.mensaje.data}', 1, '{fecha}')"

            conn.execute(add_consulta)
            conn.commit()
            conn.close()
            flash("Tu consulta se envio correctamente","success")
            return redirect(url_for('home'))
        else:
            return render_template("Contacto.html", padim=id_padim, form=form, title='contacto')
    else:
        form = Ver_consultas()
        conn = sqlite3.connect('PADIM.db')
        if form.validate_on_submit():
            consulta_mail = conn.execute(f"SELECT mail FROM consultas WHERE id_consulta={form.id_consulta.data}")
            mail =  consulta_mail.fetchall()
            enviar_respuesta(mail[0],form.respuesta.data)
            conn.execute(f"UPDATE consultas SET respondida = 1 WHERE id_consulta = {form.id_consulta.data}")
            conn.commit()
        consulta_consultas = conn.execute("SELECT * FROM consultas WHERE respondida=0")
        consultas = consulta_consultas.fetchall()

        return render_template("VerConsultas.html", padim=id_padim, title='contacto', form=form, consultas=consultas)


#Enruto para LogOut
@app.route("/logout", methods=['POST', 'GET'])
def logout():
    session.pop("padim", None)
    flash("Se cerro secion correctamente", "info")
    return redirect(url_for('home'))


#Enruto para login
@app.route("/login", methods=['POST', 'GET'])
def login():
    form = Login_form()
    if form.validate_on_submit():
        #Chequear si es un empleado
        if form.id_padim.data == 'empleado':
            if form.password.data == 'empleado123':
                session.permanent = True
                session["padim"] = 'empleado'
                flash('Logueado correctamente como empleado', 'success')
                return redirect(url_for('home'))
            else:
                flash('Error, datos erroneos', 'danger')
                return redirect(url_for('login'))
        else: #Para cuando no es un empleado
            conn = sqlite3.connect('PADIM.db')
            consulta_padims = conn.execute("SELECT id_padim FROM usuarios")
            id_padims = consulta_padims.fetchall()
            for id_padim in id_padims:
                if form.id_padim.data == id_padim[0]:
                    consulta_contraseñas = conn.execute(f"SELECT contraseña FROM usuarios WHERE id_padim = {int(form.id_padim.data)}")
                    contraseñas = consulta_contraseñas.fetchall()
                    for contraseña in contraseñas:
                        if  contraseña[0] == form.password.data:
                            session.permanent = True
                            session["padim"] = form.id_padim.data
                            conn.close()
                            flash('Logueado correctamente', 'success')
                            return redirect(url_for('home'))

                    flash('Error, datos erroneos', 'danger')
                    return redirect(url_for('login'))
            flash('Error, datos erroneos', 'danger')
            return redirect(url_for('login'))
    else:
        return render_template("LogIn.html", title='inicio de seción', form=form)

#Enruto para signup
@app.route("/signup", methods=['POST', 'GET'])
def signup():
    if logueado():
        id_padim = session["padim"]
    else:
        id_padim = None
    form = Register_form()
    if form.validate_on_submit():
        conn = sqlite3.connect('PADIM.db')
        consulta_padims = conn.execute("SELECT id_padim FROM usuarios")
        id_padims = consulta_padims.fetchall()
        for id_padim in id_padims:
            if form.id_padim.data == id_padim[0]:
                conn.close()
                flash('Ya hay una cuenta para ese PADIM, proba iniciando secion', 'warning')
                return render_template("SignUp.html", padim=id_padim, title='crear cuenta', form=form)

            consulta_emails = conn.execute("SELECT mail FROM usuarios")
            emails = consulta_emails.fetchall()
            for email in emails:
                if form.email.data == email[0]:
                    conn.close()
                    flash('Ya hay una cuenta para ese email, proba iniciando secion', 'warning')
                    return render_template("SignUp.html", padim=id_padim, title='crear cuenta', form=form)

        insertar_usuario = f'INSERT INTO usuarios (mail, id_padim, contraseña) \
                            VALUES ("{form.email.data}", "{form.id_padim.data}", "{form.password.data}")'
        conn.execute(insertar_usuario)
        conn.commit()

        for i in range(1,7):
            crear_medicamentos = f'INSERT INTO padim_tubos (id_padim, id_tubo) \
                                    VALUES ({form.id_padim.data}, {i})'
            conn.execute(crear_medicamentos)
            conn.commit()
        conn.close()
        flash(f'Cuenta creada para el padim: {form.id_padim.data} Inicie secion', 'success')
        return redirect(url_for('login'))
    else:
        return render_template("SignUp.html", padim=id_padim,title='crear cuenta', form=form)


#Enruto para el node
@app.route("/node", methods=['GET'])
def node():

    if request.method == 'GET':
        #ALMACENO GENERALIDADES
        IDPADIMTUBO = request.args.get('PadimTuboId')
        PADIMID = request.args.get('PadimId')
        PATUBO = request.args.get('PaTubo')
        DIAPHP = request.args.get('Dia')
        TUBOST = "padim_tubos"
        TOMAT = "tomas"
        DISPT = "dispensacion"
        USERT = "usuarios"

        #ALMACENO PARA LA SIMULACIÓN DE CARGA
        CARGA1 = request.args.get('input1')
        CARGA2 = request.args.get('input2')
        CARGA3 = request.args.get('input3')
        CARGA4 = request.args.get('input4')
        CARGA5 = request.args.get('input5')
        CARGA6 = request.args.get('input6')
        MENSAJEALARMA = request.args.get('nOMbreAl')

        #GET ID PADIM-TUBO
        GETIDPT = request.args.get('GetIdPT')

        #CHEQUEO DISPENSADO
        DISPCHECK = request.args.get('DispChk')

        #CHEQUEO CARGA
        CARGACHECK = request.args.get('CargaChk')

        #ACTUALIZACION DE MEDICAMENTOS
        CARGAEND = request.args.get('CargaEnd')
        PAST = request.args.get('Past')
        CTDAD = request.args.get('Ctdad')

        #CHEQUEO ALARMAS
        ALARMASCHECK = request.args.get('AlarmaChk')

        #CHEQUEO TIEMPO
        TIMECHECK = request.args.get('TimeChk')

        #TOMA Y DISPENSADO
        TOMA = request.args.get('Toma')
        DISP = request.args.get('Disp')
        FECHAPHP = request.args.get('Fecha')

        #ENVIAR EMAIL
        SEMAIL = request.args.get('Semail')
        CASEMAIL = request.args.get('CaseMail')

        #return f"{TIMECHECK}-{PADIMID}"

        #
        #SIMULACION DE CARGA
        #
        if MENSAJEALARMA != None:
            conn = sqlite3.connect('PADIM.db')
            MENSAJESQL = f"UPDATE {TUBOST} SET mensaje={MENSAJEALARMA} WHERE id_padim_tubo={IDPADIMTUBO}"
            conn.execute(MENSAJESQL)
            conn.commit()
            conn.close()


        if CARGA1 == '1' or CARGA1 == '0':
            conn = sqlite3.connect('PADIM.db')
            MENSAJESQL = f"UPDATE {TUBOST} SET carga={CARGA1} WHERE id_tubo=1 AND id_padim={PADIMID}"
            conn.execute(MENSAJESQL)
            conn.commit()
            conn.close()

        if CARGA2 == '1' or CARGA2 == '0':
            conn = sqlite3.connect('PADIM.db')
            MENSAJESQL = f"UPDATE {TUBOST} SET carga={CARGA2} WHERE id_tubo=2 AND id_padim={PADIMID}"
            conn.execute(MENSAJESQL)
            conn.commit()
            conn.close()

        if CARGA3 == '1' or CARGA3 == '0':
            conn = sqlite3.connect('PADIM.db')
            MENSAJESQL = f"UPDATE {TUBOST} SET carga={CARGA3} WHERE id_tubo=3 AND id_padim={PADIMID}"
            conn.execute(MENSAJESQL)
            conn.commit()
            conn.close()

        if CARGA4 == '1' or CARGA4 == '0':
            conn = sqlite3.connect('PADIM.db')
            MENSAJESQL = f"UPDATE {TUBOST} SET carga={CARGA4} WHERE id_tubo=4 AND id_padim={PADIMID}"
            conn.execute(MENSAJESQL)
            conn.commit()
            conn.close()

        if CARGA5 == '1' or CARGA5 == '0':
            conn = sqlite3.connect('PADIM.db')
            MENSAJESQL = f"UPDATE {TUBOST} SET carga={CARGA5} WHERE id_tubo=5 AND id_padim={PADIMID}"
            conn.execute(MENSAJESQL)
            conn.commit()
            conn.close()

        if CARGA6 == '1' or CARGA6 == '0':
            conn = sqlite3.connect('PADIM.db')
            MENSAJESQL = f"UPDATE {TUBOST} SET carga={CARGA6} WHERE id_tubo=6 AND id_padim={PADIMID}"
            conn.execute(MENSAJESQL)
            conn.commit()
            conn.close()



        #
        #GET ID PADIM TUBO
        #
        if GETIDPT == '1':
            GETIDPT = '0'
            conn = sqlite3.connect('PADIM.db')

            MENSAJESQL = f"SELECT id_tubo, id_padim_tubo FROM {TUBOST} WHERE id_padim={PADIMID}"
            SEND = conn.execute(MENSAJESQL)
            ANSQL= SEND.fetchall()

            MENSAJESQL = f"SELECT COUNT(*) FROM {TUBOST} WHERE id_padim={PADIMID}"
            SEND = conn.execute(MENSAJESQL)
            CANTIDAD = SEND.fetchone()
            AUX=ANSQL[0]
            TONODE=""

            if CANTIDAD[0]>=1:
                for i in range (CANTIDAD[0]):
                    TONODE =f"{TONODE}{ANSQL[i-1][0]}-{ANSQL[i-1][1]};"
                return f"{TONODE}#"
            else:
                return f"N#"

            conn.close()

        #
        #CHEQUEO DISPENSADO
        #
        if DISPCHECK == '1':
            DISPCHECK = '0'

            conn = sqlite3.connect('PADIM.db')

            MENSAJESQL = f"SELECT hora FROM {DISPT} WHERE id_padim_tubo={PATUBO} AND dia='{DIAPHP}' ORDER BY hora DESC"
            SEND = conn.execute(MENSAJESQL)
            ANSQL= SEND.fetchall()
            #return f"{ANSQL}"
            MENSAJESQL = f"SELECT COUNT(*) FROM {DISPT} WHERE id_padim_tubo={PATUBO} AND dia='{DIAPHP}'"
            SEND = conn.execute(MENSAJESQL)
            CANTIDAD = SEND.fetchone()

            TONODE=""

            if CANTIDAD[0]>=1:
                TONODE= ANSQL[0][0]
                return f"{TONODE}#"
            else:
                return f"N#"

            conn.close()

        #
        #CHEQUEO CARGA
        #
        if CARGACHECK == '1':
            CARGACHECK = '0'
            conn = sqlite3.connect('PADIM.db')

            MENSAJESQL = f"SELECT id_tubo FROM {TUBOST} WHERE carga=1 AND id_padim={PADIMID}"
            SEND = conn.execute(MENSAJESQL)
            ANSQL= SEND.fetchone()

            MENSAJESQL = f"SELECT COUNT(*) FROM {TUBOST} WHERE carga=1 AND id_padim={PADIMID}"
            SEND = conn.execute(MENSAJESQL)
            CANTIDAD = SEND.fetchone()

            TONODE=""


            if CANTIDAD[0]>=1:
                TONODE= ANSQL[0]
                return f"{TONODE}#"
            else:
                return f"N#"

            conn.close()

        #
        #ACTUALIZACIÓN DE MEDICAMENTOS
        #
        if CARGAEND == '1':
            CARGAEND = '0'
            conn = sqlite3.connect('PADIM.db')

            MENSAJESQL = f"UPDATE {TUBOST} SET cantidad_disponible={CTDAD}, carga=0 WHERE id_tubo={PAST} AND id_padim={PADIMID}"
            conn.execute(MENSAJESQL)

            conn.commit()
            conn.close()

        #
        #CHEQUEO ALARMAS
        #
        if ALARMASCHECK == '1':
            ALARMASCHECK = '0'
            conn = sqlite3.connect('PADIM.db')

            MENSAJESQL = f"SELECT id_tubo, horario, dias, cantidad_dispensar, repeticion, mensaje, toma_libre, nombre, hab_dispensar FROM {TUBOST} WHERE dias IS NOT NULL AND id_padim={PADIMID}"
            SEND = conn.execute(MENSAJESQL)
            ANSQL= SEND.fetchall()

            MENSAJESQL = f"SELECT COUNT(*) FROM {TUBOST} WHERE nombre IS NOT NULL AND id_padim={PADIMID}"
            SEND = conn.execute(MENSAJESQL)
            CANTIDAD = SEND.fetchone()

            TONODE=""
            if CANTIDAD[0]>=1:
                for i in range (CANTIDAD[0]):
                    TONODE =f"{TONODE}T{ANSQL[i-1][0]};{ANSQL[i-1][1]};{ANSQL[i-1][2]};{ANSQL[i-1][3]};{ANSQL[i-1][4]};{ANSQL[i-1][5]};{ANSQL[i-1][6]};{ANSQL[i-1][7]};{ANSQL[i-1][8]}?"
                return f"{TONODE}#"
            else:
                return f"N#"
            conn.close()

        #
        #CHEQUEO TIEMPO
        #
        if TIMECHECK == '1':
            TIMECHECK = '0'
            conn = sqlite3.connect('PADIM.db')

            MENSAJESQL = f"UPDATE {TUBOST} SET tiempo=CURRENT_TIMESTAMP WHERE id_padim={PADIMID}"
            conn.execute(f"{MENSAJESQL}")
            conn.commit()

            MENSAJESQL = f"SELECT tiempo FROM {TUBOST} WHERE id_padim={PADIMID}"
            SEND = conn.execute(MENSAJESQL)
            ANSQL = SEND.fetchone()

            DIACT1=datetime.today().strftime('%A')
            DIACT2=DIACT1[0:3]
            TONODE=f"H{DIACT2};{ANSQL[0]}"
            return f"{TONODE}#"

            conn.close()

        #
        #AVISO DE TOMA
        #
        if TOMA == '1':
            TOMA = '0'
            conn = sqlite3.connect('PADIM.db')

            if FECHAPHP != "":
                MENSAJESQL = f"INSERT INTO {TOMAT}(id_padim_tubo, id_padim, hora, dia) VALUES({IDPADIMTUBO},{PADIMID},'{FECHAPHP}', '{DIA}')"
            else:
                DIACT1=datetime.today().strftime('%A')
                DIACT2=DIACT1[0:3]
                if DIACT2 == "Mon":
                    DIA=1
                elif DIACT2 == "Tue":
                    DIA=2
                elif DIACT2 == "Wed":
                    DIA=3
                elif DIACT2 == "Thu":
                    DIA=4
                elif DIACT2 == "Fri":
                    DIA=5
                elif DIACT2 == "Sat":
                    DIA=6
                elif DIACT2 == "Sun":
                    DIA=7

                MENSAJESQL = f"INSERT INTO {TOMAT}(id_padim_tubo, id_padim, hora, dia) VALUES({IDPADIMTUBO},{PADIMID},CURRENT_TIMESTAMP, '{DIA}'')"

            conn.execute(MENSAJESQL)
            conn.commit()
            conn.close()

        #
        #AVISO DE DISPENSADO
        #
        if DISP == '1':
            DISP = '0'
            conn = sqlite3.connect('PADIM.db')

            if FECHAPHP != "":
                MENSAJESQL = f"INSERT INTO {DISPT}(id_padim_tubo, id_padim, hora, dia) VALUES({IDPADIMTUBO},{PADIMID},'{FECHAPHP}', '{DIA}')"
            else:
                DIACT1=datetime.today().strftime('%A')
                DIACT2=DIACT1[0:3]
                if DIACT2 == "Mon":
                    DIA=1
                elif DIACT2 == "Tue":
                    DIA=2
                elif DIACT2 == "Wed":
                    DIA=3
                elif DIACT2 == "Thu":
                    DIA=4
                elif DIACT2 == "Fri":
                    DIA=5
                elif DIACT2 == "Sat":
                    DIA=6
                elif DIACT2 == "Sun":
                    DIA=7

                MENSAJESQL = f"INSERT INTO {DISPT}(id_padim_tubo, id_padim, hora, dia) VALUES({IDPADIMTUBO},{PADIMID},CURRENT_TIMESTAMP, '{DIA}'')"

            conn.execute(MENSAJESQL)
            conn.commit()
            conn.close()
        #
        #ENVIAR EMAIL
        #
        if SEMAIL == '1':
            SEMAIL = '0'
            conn = sqlite3.connect('PADIM.db')

            MENSAJESQL = f"SELECT nombre FROM {TUBOST} WHERE id_padim_tubo={PATUBO}"
            SEND = conn.execute(MENSAJESQL)
            NOMBREMEDICAMENTO = SEND.fetchone()

            MENSAJESQL= f"SELECT mail FROM {USERT} WHERE id_padim={PADIMID}"
            SEND = conn.execute(MENSAJESQL)
            TOEMAIL = SEND.fetchone()

            MENSAJESQL= f"SELECT cantidad_disponible FROM {TUBOST} WHERE id_padim_tubo={PATUBO}"
            SEND = conn.execute(MENSAJESQL)
            UDISP = SEND.fetchone()

            if CASEMAIL == '1':#CASO FALTA TOMAR
                EMENSAJE = f"Nos comunicamos para informar que el medicamento {NOMBREMEDICAMENTO} fue dispensado hace mas de 15 minutos, pero aun no fue tomado."
                EHEADER = "ALERTA: MEDICAMENTO SIN TOMAR"
                server = smtplib.SMTP('64.233.184.108')
                server.starttls()
                server.login('proyecto6to2021@gmail.com', '2021fernando')
                msg = f"Subject: {EHEADER}\n\n{EMENSAJE}"
                server.sendmail('proyecto6to2021@gmail.com', TOEMAIL, msg)
                server.close()

            elif CASEMAIL == '2': #CASO POCAS PASTILLAS DISPONIBLES
                EMENSAJE = f"Nos comunciamos para informar que quedan pocas unidades del medicamento {NOMBREMEDICAMENTO}. Unidades restantes: {UDISP}."
                EHEADER = "ALERTA: ESCACEZ DE MEDICAMENTOS"
                server = smtplib.SMTP('64.233.184.108')
                server.starttls()
                server.login('proyecto6to2021@gmail.com', '2021fernando')
                msg = f"Subject: {EHEADER}\n\n{EMENSAJE}"
                server.sendmail('proyecto6to2021@gmail.com', TOEMAIL, msg)
                server.close()

            conn.close()
        return  "no entro a ningun lado bro"

    else:
        return 'oknt'

if __name__ == "__main__":
    app.run(debug=True)