<!-- filepath: /Users/cuixueyong/VscodeWorkSpace/ecloud_web/frontend/src/components/Search.vue -->
<template>
  <div class="search-container">
    <el-card class="search-card">
      <h1 class="title">移动云帮助中心搜索</h1>
      
      <el-input
        v-model="query"
        placeholder="请输入您的问题，例如：如何创建云主机？"
        :suffix-icon="Search"
        @keyup.enter="handleSearch"
        class="search-input"
      >
        <template #append>
          <el-button type="primary" @click="handleSearch" :loading="loading">
            搜索
          </el-button>
        </template>
      </el-input>

      <div v-if="result" class="result-container">
        <el-card class="result-card">
          <template #header>
            <div class="result-header">
              <h3>最佳匹配</h3>
              <el-tag type="success">置信度: {{ (result.confidence * 100).toFixed(2) }}%</el-tag>
            </div>
          </template>
          
          <h4>{{ result.title }}</h4>
          <p class="answer">{{ result.answer }}</p>
          <el-link 
            :href="result.source_url" 
            target="_blank"
            type="primary"
          >
            查看原文
          </el-link>
        </el-card>

        <div v-if="result.alternative_results?.length" class="alternative-results">
          <h3>相关推荐</h3>
          <el-card 
            v-for="(alt, index) in result.alternative_results" 
            :key="index"
            class="alt-card"
          >
            <h4>{{ alt.title }}</h4>
            <div class="alt-footer">
              <el-tag size="small">相关度: {{ (alt.score * 100).toFixed(2) }}%</el-tag>
              <el-link :href="alt.url" target="_blank" type="info">
                查看详情
              </el-link>
            </div>
          </el-card>
        </div>
      </div>
    </el-card>
  </div>
</template>

<script setup>
import { ref } from 'vue'
import { Search } from '@element-plus/icons-vue'
import { ElMessage } from 'element-plus'
import axios from 'axios'

const query = ref('')
const loading = ref(false)
const result = ref(null)

const handleSearch = async () => {
  if (!query.value.trim()) {
    ElMessage.warning('请输入搜索问题')
    return
  }

  loading.value = true
  try {
    const response = await axios.post('http://localhost:8000/api/search', {
      query: query.value
    })
    result.value = response.data
  } catch (error) {
    ElMessage.error(error.response?.data?.detail || '搜索出错')
  } finally {
    loading.value = false
  }
}
</script>

<style scoped>
.search-container {
  max-width: 800px;
  margin: 2rem auto;
  padding: 0 1rem;
}

.title {
  text-align: center;
  color: #303133;
  margin-bottom: 2rem;
}

.search-card {
  margin-bottom: 2rem;
}

.search-input {
  margin: 2rem 0;
}

.result-container {
  margin-top: 2rem;
}

.result-header {
  display: flex;
  justify-content: space-between;
  align-items: center;
}

.answer {
  white-space: pre-wrap;
  line-height: 1.6;
  margin: 1rem 0;
  color: #606266;
}

.alternative-results {
  margin-top: 2rem;
}

.alt-card {
  margin-top: 1rem;
}

.alt-footer {
  display: flex;
  justify-content: space-between;
  align-items: center;
  margin-top: 1rem;
}
</style>