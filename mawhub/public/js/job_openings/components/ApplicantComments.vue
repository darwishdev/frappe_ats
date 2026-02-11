<template>
  <div class="applicant-comments">
    <div class="comments-container">
      <div class="comments-header">
        <h3>Comments</h3>
        <button class="btn btn-sm btn-primary" @click="addComment">
          <span class="fa fa-comment"></span> Add Comment
        </button>
      </div>
      
      <div v-if="loading" class="comments-loading">
        <div style="text-align: center; padding: 40px; color: #888;">
          Loading comments...
        </div>
      </div>
      <div v-else-if="comments.length > 0" class="comments-list">
        <div
          v-for="comment in comments"
          :key="comment.name"
          class="comment-item"
        >
          <div class="comment-avatar">
            {{ comment.comment_by?.charAt(0).toUpperCase() || comment.owner?.charAt(0).toUpperCase() }}
          </div>
          <div class="comment-body">
            <div class="comment-header">
              <span class="comment-author">{{ comment.comment_by || comment.owner }}</span>
              <span class="comment-date">{{ formatDate(comment.creation) }}</span>
            </div>
            <div class="comment-content" v-html="comment.content"></div>
          </div>
        </div>
      </div>
      <div v-else class="comments-empty">
        <p>No comments yet. Start the conversation!</p>
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
const comments = ref([]);

watch(
  () => props.candidate,
  async (newCandidate) => {
    if (newCandidate?.job_applicant) {
      await fetchComments(newCandidate.job_applicant);
    } else {
      comments.value = [];
    }
  },
  { immediate: true }
);

async function fetchComments(applicantId) {
  if (!applicantId) return;
  
  loading.value = true;
  
  frappe.call({
    method: 'frappe.desk.reportview.get',
    args: {
      doctype: 'Comment',
      fields: [
        "`tabComment`.`name`",
        "`tabComment`.`owner`",
        "`tabComment`.`creation`",
        "`tabComment`.`modified`",
        "`tabComment`.`modified_by`",
        "`tabComment`.`comment_email`",
        "`tabComment`.`comment_by`",
        "`tabComment`.`reference_doctype`",
        "`tabComment`.`content`",
        "`tabComment`.`comment_type`"
      ],
      filters: [["Comment", "reference_name", "=", applicantId]]
    },
    callback: function(res) {
      loading.value = false;
      if (res.message && res.message.values) {
        // Map the array values to objects based on keys
        const keys = res.message.keys || [];
        comments.value = res.message.values.map(valueArray => {
          const commentObj = {};
          keys.forEach((key, index) => {
            commentObj[key] = valueArray[index];
          });
          return commentObj;
        });
      } else {
        comments.value = [];
      }
    },
    error: function(err) {
      loading.value = false;
      comments.value = [];
      console.error('Failed to load comments:', err);
    }
  });
}

function addComment() {
  if (!props.candidate) return;
  
  const dialog = new frappe.ui.Dialog({
    title: `Add Comment`,
    fields: [
      {
        fieldtype: 'Small Text',
        fieldname: 'comment',
        label: 'Comment',
        reqd: 1
      }
    ],
    primary_action_label: 'Add',
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
            message: 'Comment added successfully',
            indicator: 'green'
          });
          dialog.hide();
          fetchComments(props.candidate.job_applicant);
        },
        error: function(err) {
          console.error('Failed to add comment:', err);
          frappe.msgprint({
            title: 'Error',
            message: 'Failed to add comment',
            indicator: 'red'
          });
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
    day: 'numeric',
    hour: '2-digit',
    minute: '2-digit'
  });
}
</script>

<style scoped>
.applicant-comments {
  padding: 8px;
}

.comments-container {
  max-height: calc(100vh - 400px);
  overflow-y: auto;
}

.comments-header {
  display: flex;
  justify-content: space-between;
  align-items: center;
  margin-bottom: 16px;
  padding-bottom: 12px;
  border-bottom: 2px solid #e5e7eb;
}

.comments-header h3 {
  font-size: 18px;
  font-weight: 700;
  color: #111827;
  margin: 0;
}

.comments-loading,
.comments-empty {
  min-height: 200px;
  display: flex;
  align-items: center;
  justify-content: center;
  color: #888;
}

.comments-list {
  display: flex;
  flex-direction: column;
  gap: 16px;
}

.comment-item {
  display: flex;
  gap: 12px;
  background: #f9fafb;
  border-radius: 8px;
  padding: 16px;
  border: 1px solid #e5e7eb;
}

.comment-avatar {
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
  flex-shrink: 0;
}

.comment-body {
  flex: 1;
  min-width: 0;
}

.comment-header {
  display: flex;
  justify-content: space-between;
  align-items: center;
  margin-bottom: 8px;
}

.comment-author {
  font-size: 14px;
  font-weight: 600;
  color: #111827;
}

.comment-date {
  font-size: 12px;
  color: #9ca3af;
}

.comment-content {
  font-size: 14px;
  line-height: 1.6;
  color: #4b5563;
  word-wrap: break-word;
}

.comment-content :deep(p) {
  margin: 0;
}

/* Dark Mode Styles */
[data-theme="dark"] .comments-header h3 {
  color: #f0f0f0;
}

[data-theme="dark"] .comments-header {
  border-bottom-color: #3a3a3a;
}

[data-theme="dark"] .comments-loading,
[data-theme="dark"] .comments-empty {
  color: #9ca3af;
}

[data-theme="dark"] .comment-item {
  background: #2a2a2a;
  border-color: #3a3a3a;
}

[data-theme="dark"] .comment-avatar {
  background: #667eea;
}

[data-theme="dark"] .comment-author {
  color: #f0f0f0;
}

[data-theme="dark"] .comment-date {
  color: #6b7280;
}

[data-theme="dark"] .comment-content {
  color: #d1d5db;
}
</style>
