import os
from flask import redirect, render_template, request, session



def loggedIn_user():
    return session["user_id"]