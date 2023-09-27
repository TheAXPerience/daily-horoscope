from authenticate.models import DATEOFBIRTH_FORMAT

def test_custom_user_serialize(user1):
    data = user1.serialize()

    assert 'username' in data and data['username'] == user1.username
    assert 'email' in data and data['email'] == user1.email
    assert 'date_of_birth' in data and data['date_of_birth'] == user1.date_of_birth.strftime(DATEOFBIRTH_FORMAT)
    assert 'accept_tos' not in data
    assert 'password' not in data

def test_user_profile_serialize_inclusive(profile1):
    prof, user = profile1
    data = prof.serialize()

    assert 'username' in data and data['username'] == user.username
    assert 'description' in data and data['description'] == prof.description
    assert 'subscribed_to_newsletter' in data and data['subscribed_to_newsletter'] == prof.subscribed_to_newsletter
    assert 'email' in data and data['email'] == user.email
    assert 'date_of_birth' in data and data['date_of_birth'] == user.date_of_birth.strftime(DATEOFBIRTH_FORMAT)

def test_user_profile_serialize_exclusive(profile2):
    prof, user = profile2
    data = prof.serialize()

    assert 'username' in data and data['username'] == user.username
    assert 'description' in data and data['description'] == prof.description
    assert 'subscribed_to_newsletter' in data and data['subscribed_to_newsletter'] == prof.subscribed_to_newsletter
    assert 'email' not in data
    assert 'date_of_birth' not in data
