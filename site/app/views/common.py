from flask import flash


def display_errors(errors):
    for error in errors:
        for item in errors[error]:
            flash('%s: %s' % (error, item), 'warning')