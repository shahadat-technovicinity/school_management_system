from celery import shared_task
from .models import StudentPersonalInfo, GeneratedIDCard
from .services import generate_card_image_service

@shared_task
def batch_generate_cards_task(student_ids, template_id, user_id):
    count = 0
    for sid in student_ids:
        try:
            student = StudentPersonalInfo.objects.get(id=sid)
            
            # Generate Image
            image_file = generate_card_image_service(student, template_id)
            
            # Save Record
            GeneratedIDCard.objects.create(
                student=student,
                template_id=template_id,
                card_image=image_file,
                generated_by_id=user_id
            )
            count += 1
        except Exception as e:
            print(f"Failed to generate for {sid}: {e}")
            
    return f"Generated {count} cards."