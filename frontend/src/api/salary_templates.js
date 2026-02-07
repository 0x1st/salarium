import api from '../utils/axios'

export async function getSalaryTemplate(personId) {
  const { data } = await api.get(`/salary-templates/${personId}`)
  return data
}

export async function upsertSalaryTemplate(personId, payload) {
  const { data } = await api.put(`/salary-templates/${personId}`, payload)
  return data
}

export async function deleteSalaryTemplate(personId) {
  const { data } = await api.delete(`/salary-templates/${personId}`)
  return data
}
