from celery import shared_task
from django_celery_results.models import TaskResult
from .models import StudentPersonalInfo, GeneratedIDCard
from .services import generate_card_image_service

@shared_task(bind=True)
def batch_generate_cards_task(self, student_ids, template_id, user_id):
    """
    bind=True gives access to self for progress updates
    """
    total = len(student_ids)
    count = 0
    failed = []
    
    for i, sid in enumerate(student_ids):
        try:
            # Update progress
            self.update_state(
                state='PROGRESS',
                meta={'current': i + 1, 'total': total}
            )
            
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
            failed.append(sid)
            print(f"Failed to generate for {sid}: {e}")
    
    return {
        'total': total,
        'processed': count,
        'failed': len(failed),
        'failed_ids': failed
    }