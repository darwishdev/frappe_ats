<template>
  <div class="applicant-review">
    <div class="review-container">
      <div class="review-header">
        <h3>Candidate Review</h3>
        <button class="btn btn-sm btn-primary" @click="addReview">
          <span class="fa fa-plus"></span> Add Review
        </button>
      </div>
      
      <div v-if="loading" class="review-loading">
        <div style="text-align: center; padding: 40px; color: #888;">
          Loading reviews...
        </div>
      </div>
      <div v-else-if="reviews.length > 0" class="review-list">
        <div
          v-for="review in reviews"
          :key="review.name"
          class="review-item"
        >
          <div class="review-header-info">
            <div class="review-author">
              <div class="review-avatar">
                {{ review.owner?.charAt(0).toUpperCase() }}
              </div>
              <div>
                <div class="review-author-name">{{ review.owner }}</div>
                <div class="review-date">{{ formatDate(review.creation) }}</div>
              </div>
            </div>
            <div v-if="review.rating" class="review-rating">
              <span v-for="star in 5" :key="star" class="star" :class="{ filled: star <= review.rating }">
                ★
              </span>
            </div>
          </div>
          <div v-if="review.comment" class="review-content">
            {{ review.comment }}
          </div>
        </div>
      </div>
      <div v-else class="review-empty">
        <p>No reviews yet. Be the first to review this candidate!</p>
      </div>
    </div>
  </div>
</template>

<script setup>
import { ref, watch, getCurrentInstance } from 'vue';

const { proxy } = getCurrentInstance();
const frappe = proxy.$frappe;

const props = defineProps({
  candidate: {
    type: Object,
    default: null
  }
});

const loading = ref(false);
const reviews = ref([]);

watch(
  () => props.candidate,
  async (newCandidate) => {
    if (newCandidate?.job_applicant) {
      await fetchReviews(newCandidate.job_applicant);
    } else {
      reviews.value = [];
    }
  },
  { immediate: true }
);

async function fetchReviews(applicantId) {
  if (!applicantId) return;
  
  loading.value = true;
  
  // Fetch comments that are marked as reviews
  frappe.call({
    method: 'frappe.desk.reportview.get',
    args: {
      doctype: 'Comment',
      fields: [
        "`tabComment`.`name`",
        "`tabComment`.`owner`",
        "`tabComment`.`creation`",
        "`tabComment`.`comment_email`",
        "`tabComment`.`comment_by`",
        "`tabComment`.`content`",
        "`tabComment`.`comment_type`"
      ],
      filters: [
        ["Comment", "reference_name", "=", applicantId],
        ["Comment", "comment_type", "=", "Comment"]
      ]
    },
    callback: function(res) {
      loading.value = false;
      if (res.message && res.message.values) {
        // Map the array values to objects based on keys
        const keys = res.message.keys || [];
        reviews.value = res.message.values.map(valueArray => {
          const reviewObj = {};
          keys.forEach((key, index) => {
            reviewObj[key] = valueArray[index];
          });
          return reviewObj;
        });
      } else {
        reviews.value = [];
      }
    },
    error: function(err) {
      loading.value = false;
      reviews.value = [];
      console.error('Failed to load reviews:', err);
    }
  });
}

function addReview() {
  if (!props.candidate) return;
  
  const dialog = new frappe.ui.Dialog({
    title: `Review ${props.candidate.job_applicant}`,
    fields: [
      {
        fieldtype: 'Rating',
        fieldname: 'rating',
        label: 'Rating',
        reqd: 1
      },
      {
        fieldtype: 'Small Text',
        fieldname: 'comment',
        label: 'Review Comments',
        reqd: 1
      }
    ],
    primary_action_label: 'Submit Review',
    primary_action: (values) => {
      frappe.call({
        method: 'frappe.desk.form.utils.add_comment',
        args: {
          reference_doctype: 'Job Applicant',
          reference_name: props.candidate.job_applicant,
          content: values.comment,
          comment_email: frappe.session.user,
          comment_by: frappe.session.user_fullname
        },
        callback: function() {
          frappe.show_alert({
            message: 'Review added successfully',
            indicator: 'green'
          });
          dialog.hide();
          fetchReviews(props.candidate.job_applicant);
        }
      });
    }
  });
  
  dialog.show();
}

function formatDate(dateStr) {
  if (!dateStr) return '';
  const date = new Date(dateStr);
  return date.toLocaleDateString('en-US', { 
    year: 'numeric', 
    month: 'short', 
    day: 'numeric'
  });
}
</script>

<style scoped>
.applicant-review {
  padding: 8px;
}

.review-container {
  max-height: calc(100vh - 400px);
  overflow-y: auto;
}

.review-header {
  display: flex;
  justify-content: space-between;
  align-items: center;
  margin-bottom: 16px;
  padding-bottom: 12px;
  border-bottom: 2px solid #e5e7eb;
}

.review-header h3 {
  font-size: 18px;
  font-weight: 700;
  color: #111827;
  margin: 0;
}

.review-loading,
.review-empty {
  min-height: 200px;
  display: flex;
  align-items: center;
  justify-content: center;
  color: #888;
}

.review-list {
  display: flex;
  flex-direction: column;
  gap: 16px;
}

.review-item {
  background: #f9fafb;
  border-radius: 8px;
  padding: 16px;
  border: 1px solid #e5e7eb;
}

.review-header-info {
  display: flex;
  justify-content: space-between;
  align-items: flex-start;
  margin-bottom: 12px;
}

.review-author {
  display: flex;
  align-items: center;
  gap: 12px;
}

.review-avatar {
  width: 40px;
  height: 40px;
  border-radius: 50%;
  background: #667eea;
  color: white;
  display: flex;
  align-items: center;
  justify-content: center;
  font-size: 18px;
  font-weight: 600;
}

.review-author-name {
  font-size: 14px;
  font-weight: 600;
  color: #111827;
}

.review-date {
  font-size: 12px;
  color: #9ca3af;
}

.review-rating {
  display: flex;
  gap: 2px;
}

.star {
  color: #d1d5db;
  font-size: 20px;
}

.star.filled {
  color: #fbbf24;
}

.review-content {
  font-size: 14px;
  line-height: 1.6;
  color: #4b5563;
}

/* Dark Mode Styles */
[data-theme="dark"] .review-header h3 {
  color: #f0f0f0;
}

[data-theme="dark"] .review-header {
  border-bottom-color: #3a3a3a;
}

[data-theme="dark"] .review-loading,
[data-theme="dark"] .review-empty {
  color: #9ca3af;
}

[data-theme="dark"] .review-item {
  background: #2a2a2a;
  border-color: #3a3a3a;
}

[data-theme="dark"] .review-avatar {
  background: #667eea;
}

[data-theme="dark"] .review-author-name {
  color: #f0f0f0;
}

[data-theme="dark"] .review-date {
  color: #6b7280;
}

[data-theme="dark"] .star {
  color: #3a3a3a;
}

[data-theme="dark"] .star.filled {
  color: #fbbf24;
}

[data-theme="dark"] .review-content {
  color: #d1d5db;
}
</style>
