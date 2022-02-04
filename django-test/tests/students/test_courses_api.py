import json

import pytest
from django.urls import reverse
from rest_framework.status import HTTP_200_OK, HTTP_404_NOT_FOUND, HTTP_201_CREATED, HTTP_400_BAD_REQUEST, \
    HTTP_204_NO_CONTENT

from students.models import Course
from students.serializers import CourseSerializer


@pytest.mark.parametrize(
    ["course_id", "status_code"],
    (
        (1, HTTP_200_OK),
        (2, HTTP_404_NOT_FOUND),
    )
)
@pytest.mark.django_db
def test_retrieve(course_id, status_code, api_client, course_fixture, student_fixture):
    course = course_fixture(id=course_id)
    students = student_fixture(_quantity=3)
    course.students.set(students)

    url = reverse('courses-detail', args=[1])
    response = api_client.get(url)

    assert response.status_code == status_code
    if status_code == HTTP_200_OK:
        assert len(response.data['students']) == 3


@pytest.mark.django_db
def test_list(api_client, course_fixture, student_fixture):
    courses = course_fixture(_quantity=5)
    for course in courses:
        students = student_fixture(_quantity=2)
        course.students.set(students)

    url = reverse('courses-list')
    response = api_client.get(url)

    assert response.status_code == HTTP_200_OK
    assert len(response.data) == 5
    for course in response.data:
        assert len(course['students']) == 2



@pytest.mark.parametrize(
    ["filter_name", "filter_value", "course_value", "expected_count"],
    (
        ("id", 2, 2, 1),
        ("name", "vasya", "vasya", 1),
        ("name", "vasya", "petya", 0),
    )
)
@pytest.mark.django_db
def test_filter(filter_name, filter_value, course_value, expected_count, api_client, course_fixture, student_fixture):
    course = course_fixture(**{filter_name: course_value})
    students = student_fixture(_quantity=2)
    course.students.set(students)

    url = reverse('courses-list')
    response = api_client.get(url, {filter_name: filter_value})

    assert response.status_code == HTTP_200_OK
    assert len(response.data) == expected_count


@pytest.mark.django_db
def test_create(api_client, course_fixture, student_fixture):
    course = json.dumps(
        {
            "name": "python",
        })

    url = reverse('courses-list')
    response = api_client.post(url, data=json.loads(course))

    assert response.status_code == HTTP_201_CREATED
    assert len(Course.objects.all()) == 1
    assert Course.objects.first().name == "python"


@pytest.mark.django_db
def test_update(api_client, course_fixture, student_fixture):
    course = course_fixture(id=1, name="c++")

    update_course = json.dumps(
        {
            "name": "python",
        })

    url = reverse('courses-detail', args=[1])
    response = api_client.put(url, data=json.loads(update_course))

    assert response.status_code == HTTP_200_OK
    assert len(Course.objects.all()) == 1
    assert Course.objects.first().name == "python"


@pytest.mark.django_db
def test_delete(api_client, course_fixture, student_fixture):
    course = course_fixture(id=1, name="c++")

    url = reverse('courses-detail', args=[1])
    response = api_client.delete(url)

    assert response.status_code == HTTP_204_NO_CONTENT


@pytest.mark.parametrize(
    ["max_count", "students_count", "expected_status"],
    (
        (2, 1, HTTP_200_OK),
        (2, 2, HTTP_400_BAD_REQUEST),
    )
)
@pytest.mark.django_db
def test_max_students_for_course(max_count, students_count, expected_status, settings,
                                 api_client, student_fixture, course_fixture):
    settings.MAX_STUDENTS_PER_COURSE = max_count
    students = student_fixture(_quantity=students_count)
    course = course_fixture(id=1, students=students)

    new_student = student_fixture()
    course.students.add(new_student)
    serializer = CourseSerializer(course)

    url = reverse('courses-detail', args=[1])
    response = api_client.patch(url, data=serializer.data)

    assert response.status_code == expected_status