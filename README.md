# LND PubSub Server

This is a PubSub Server for LND, which can be used for tooling (e.g. frontends) which are useful in creating Ring of Fires.

After subscribing to specific pubkeys or channels you will get the current state and while the session is open, updates to both the node and the channel.

To test, fill in your own node pubkey and channel(s) in `app/templates/index.html` and go to [localhost:5000](http://localhost:5000/)

**Warning**: note that `Debug=True` in `app/main.py` for now.

Partly based on [StijnBTC/RingTools](https://github.com/StijnBTC/Ringtools)

## Goals
- Support multiple host OS'es by using Docker
- Make it as modular as possible
- Synchronize transport functionality

## Prepare pyenv virtualenv (for development)
1. `pyenv virtualenv 3.9.7 lnd-pubsub`
2. `pyenv activate lnd-pubsub`

## Usage without docker(-compose)
1. Create `.env` (see `.env.sample`)
2. Install requirement `pip3 install -r`
3. Run `python3 app/main.py`
4. Go to [localhost:5000](http://localhost:5000/) for the Debug page

## Usage with docker-compose
1. Create `.env` (see `.env.sample`)
2. Run `docker-compose up -d`
3. Go to [localhost:5000](http://localhost:5000/) for the Debug page

## Documentation
### Server
- [Flask-SocketIO](https://flask-socketio.readthedocs.io/en/latest/)
- [LND gRPC Python](https://github.com/lightningnetwork/lnd/blob/master/docs/grpc/python.md)

### Client
- [Socket.io Client API](https://socket.io/docs/v4/client-api/)
