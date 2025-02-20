

from flask import Flask, request, jsonify, Blueprint, render_template
from app import db, app, CareerPath, CareerQuestion, CareerSuggestions, IndustryChallenge, CareerStory

future_you_bp = Blueprint('future_you_bp', __name__)

