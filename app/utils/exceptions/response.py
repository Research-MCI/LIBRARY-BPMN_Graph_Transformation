from flask import jsonify


def success_response(data=None, message="Success", code=200):
    """
    Standar format success.
    """
    response = {
        "success": True,
        "message": message,
        "data": data,
    }
    return jsonify(response), code


def error_response(message="Error", code=400, errors=None):
    """
    Standar format error.
    """
    response = {
        "success": False,
        "message": message,
        "errors": errors,
    }
    return jsonify(response), code
