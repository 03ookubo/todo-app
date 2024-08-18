<template>
  <div class="container">
    <h1>TODO List</h1>
    <div class="tasks-container">
      <div class="tasks-section">
        <h2>未完了タスク</h2>
        <ul>
          <li v-for="todo in incompleteTodos" :key="todo.id" class="todo-item">
            <input type="checkbox" v-model="todo.completed" @change="updateTodoStatus(todo)" />
            <div class="todo-details">
              <h3>{{ todo.title }}</h3>
              <p class="date">期日: {{ formatDate(todo.dueDate) }}</p>
              <p class="details">タスクの詳細: {{ todo.details }}</p>
              <input type="checkbox" v-model="selectedTodos" :value="todo" />選択
            </div>
          </li>
        </ul>
      </div>
      <div class="tasks-section">
        <h2>完了タスク</h2>
        <ul>
          <li v-for="todo in completedTodos" :key="todo.id" class="todo-item">
            <input type="checkbox" v-model="todo.completed" @change="updateTodoStatus(todo)" />
            <div class="todo-details">
              <h3>{{ todo.title }}</h3>
              <p class="date">期日: {{ formatDate(todo.dueDate) }}</p>
              <p class="details">タスクの詳細: {{ todo.details }}</p>
              <input type="checkbox" v-model="selectedTodos" :value="todo" />選択
            </div>
          </li>
        </ul>
      </div>
    </div>

    <button v-if="!showForm" @click="showForm = true" class="add-task-button">新しいタスクを追加</button>
    <button v-if="selectedTodos.length" @click="deleteSelectedTodos" class="delete-task-button">選択したタスクを削除</button>

    <div v-if="showForm" class="form-container">
      <form @submit.prevent="addTodo" class="todo-form">
        <input v-model="newTodoTitle" placeholder="タスクタイトル" required class="input-field" />
        <input v-model="newTodoDueDate" type="date" required class="input-field" />
        <textarea v-model="newTodoDetails" placeholder="タスクの詳細" required class="textarea-field"></textarea>
        <button type="submit" class="submit-button">タスクを追加</button>
        <button type="button" @click="showForm = false" class="cancel-button">キャンセル</button>
      </form>
    </div>

    <div v-if="errorMessage" class="error">{{ errorMessage }}</div>
  </div>
</template>

<script setup lang="ts">
import { ref, computed, onMounted } from 'vue';

interface Todo {
  id: number;
  title: string;
  dueDate: string;
  details: string;
  completed: boolean;
}

const todos = ref<Todo[]>([]);
const newTodoTitle = ref('');
const newTodoDueDate = ref('');
const newTodoDetails = ref('');
const showForm = ref(false);
const errorMessage = ref('');
const selectedTodos = ref<Todo[]>([]);

const incompleteTodos = computed(() => {
  return todos.value
    .filter(todo => !todo.completed)
    .sort((a, b) => new Date(a.dueDate).getTime() - new Date(b.dueDate).getTime());
});

const completedTodos = computed(() => {
  return todos.value
    .filter(todo => todo.completed)
    .sort((a, b) => new Date(a.dueDate).getTime() - new Date(b.dueDate).getTime());
});

onMounted(async () => {
  try {
    const response = await fetch('http://localhost:5000/todos');
    if (response.ok) {
      todos.value = await response.json() as Todo[];
    } else {
      throw new Error('タスクの取得に失敗しました');
    }
  } catch (error) {
    console.error(error);
    errorMessage.value = 'タスクの読み込みに失敗しました';
  }
});

const addTodo = async () => {
  if (newTodoTitle.value.trim() === '' || newTodoDueDate.value.trim() === '' || newTodoDetails.value.trim() === '') return;

  const newTodo = {
    title: newTodoTitle.value,
    dueDate: newTodoDueDate.value,
    details: newTodoDetails.value,
    completed: false,
  };

  try {
    const response = await fetch('http://localhost:5000/todos', {
      method: 'POST',
      headers: {
        'Content-Type': 'application/json',
      },
      body: JSON.stringify(newTodo)
    });

    if (response.ok) {
      const createdTodo = await response.json() as Todo;
      todos.value.push(createdTodo);
      newTodoTitle.value = '';
      newTodoDueDate.value = '';
      newTodoDetails.value = '';
      showForm.value = false;
      errorMessage.value = '';
    } else {
      const errorText = await response.text();
      throw new Error(errorText);
    }
  } catch (error) {
    console.error('ToDo を追加できませんでした:', error);
    errorMessage.value = 'ToDo を追加できませんでした';
  }
};

const updateTodoStatus = async (todo: Todo) => {
  try {
    const response = await fetch(`http://localhost:5000/todos/${todo.id}`, {
      method: 'PUT',
      headers: {
        'Content-Type': 'application/json',
      },
      body: JSON.stringify({ completed: todo.completed })
    });

    if (!response.ok) {
      throw new Error('TODOの更新に失敗しました。');
    }
  } catch (error) {
    console.error('TODOの更新に失敗しました。:', error);
    errorMessage.value = 'TODOの更新に失敗しました。';
  }
};

const deleteSelectedTodos = async () => {
  try {
    await Promise.all(selectedTodos.value.map(async todo => {
      const response = await fetch(`http://localhost:5000/todos/${todo.id}`, {
        method: 'DELETE',
      });

      if (!response.ok) {
        throw new Error(`Failed to delete todo with id ${todo.id}`);
      }
    }));

    todos.value = todos.value.filter(todo => !selectedTodos.value.some(selected => selected.id === todo.id));
    selectedTodos.value = [];
  } catch (error) {
    console.error('Failed to delete selected todos:', error);
    errorMessage.value = 'Failed to delete selected todos';
  }
};

const formatDate = (dateString: string) => {
  if (dateString == null) {
    return "なし"
  }
  const date = new Date(dateString);
  return `${date.getFullYear()}-${String(date.getMonth() + 1).padStart(2, '0')}-${String(date.getDate()).padStart(2, '0')}`;
};
</script>

<style scoped>
/*全体 */
.container {
  max-width: 900px;
  margin: 0 auto;
  padding: 20px;
  background-color: #f4f4f9;
  border-radius: 8px;
  box-shadow: 0 0 10px rgba(0, 0, 0, 0.1);
}

/* タスクの表示エリア */
.tasks-container {
  display: flex;
  justify-content: space-between;
  gap: 20px;
}

.tasks-section {
  flex: 1;
  padding: 10px;
  background-color: #ffffff;
  border-radius: 8px;
  box-shadow: 0 0 5px rgba(0, 0, 0, 0.1);
}

h2 {
  border-bottom: 2px solid #007bff;
  padding-bottom: 10px;
  color: #333;
}

/* タスクアイテム */
.todo-item {
  list-style-type: none;
  margin: 10px 0;
  border: 1px solid #ddd;
  border-radius: 8px;
  padding: 15px;
  background-color: #f9f9f9;
  transition: background-color 0.3s, box-shadow 0.3s;
}

.todo-item:hover {
  background-color: #e2e6ea;
  box-shadow: 0 0 10px rgba(0, 0, 0, 0.1);
}

.todo-content {
  display: flex;
  align-items: flex-start;
  gap: 10px;
}

.todo-details {
  margin-left: 15px;
}

.date, .details {
  margin: 5px 0;
  font-size: 14px;
  color: #555;
}

/* ボタン */
button {
  border: none;
  border-radius: 5px;
  padding: 10px 20px;
  font-size: 16px;
  cursor: pointer;
  transition: background-color 0.3s, color 0.3s;
}

.add-task-button {
  background-color: #007bff;
  color: white;
}

.add-task-button:hover {
  background-color: #0056b3;
}

.delete-task-button {
  background-color: #dc3545;
  color: white;
}

.delete-task-button:hover {
  background-color: #c82333;
}

.submit-button {
  background-color: #28a745;
  color: white;
}

.submit-button:hover {
  background-color: #218838;
}

.cancel-button {
  background-color: #6c757d;
  color: white;
}

.cancel-button:hover {
  background-color: #5a6268;
}

/* フォーム */
.form-container {
  margin-top: 20px;
  padding: 15px;
  background-color: #ffffff;
  border-radius: 8px;
  box-shadow: 0 0 5px rgba(0, 0, 0, 0.1);
}

.todo-form {
  display: flex;
  flex-direction: column;
  gap: 10px;
}

.input-field, .textarea-field {
  padding: 10px;
  border: 1px solid #ddd;
  border-radius: 5px;
  font-size: 16px;
}

.textarea-field {
  resize: vertical;
}

/* エラーメッセージ */
.error {
  margin-top: 20px;
  color: #dc3545;
  font-size: 16px;
}
</style>


