from flask import Flask, session, redirect, url_for, render_template, request
from flask_socketio import send, SocketIO, emit, join_room, leave_room
from flask_wtf import Form 
from wtforms.fields import StringField, SubmitField
from wtforms.validators import Required

app = Flask(__name__)
app.config['SECRET_KEY'] = 'mysecret'

socketio = SocketIO(app)


class UserForm(Form):
    name = StringField('Name', validators=[Required()])
    room = StringField('Room', validators=[Required()])
    submit = SubmitField('Enter Chatroom')


@app.route('/',methods=['GET','POST'])
def index():
    form = UserForm()
    if form.validate_on_submit():
        session['name']= form.name.data
        session['room']= form.room.data
        return redirect(url_for('.chat'))
    elif request.method == 'GET':
        form.name.data = session.get('name', '')
        form.room.data = session.get('room', '')
    return render_template('index.html', form=form)

@app.route('/chat')
def chat():
    name = session.get('name','')
    room = session.get('room','')
    if name == '' or room == '':
        return redirect(url_for('.index'))
    return render_template('chat.html',name=name, room=room)

@socketio.on('joined',namespace='/chat')
def joined(message):
    room = session.get('room')
    join_room(room)
    emit('status',{'msg' : session.get('name') + ' has entered the room.'}, room=room)

@socketio.on('text', namespace='/chat')
def joined(message):
    room = session.get('room')
    emit('message', {'msg' : session.get('name') + ':' + message['msg']}, room = room)

@socketio.on('left', namespace='/chat')
def left(message):
    room = session.get('room')
    leave_room(room)
    emit('status',{'msg' : session.get('name') + ' has left the room.'}, room=room)


if __name__ == '__main__':
    socketio.run(app)