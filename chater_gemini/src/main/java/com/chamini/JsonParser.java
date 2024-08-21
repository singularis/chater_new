package com.chamini;

import org.json.JSONArray;
import org.json.JSONObject;

public class JsonParser {

    public static String extractText(String responseBody) {
        JSONObject jsonResponse = new JSONObject(responseBody);
        JSONArray candidates = jsonResponse.getJSONArray("candidates");
        if (!candidates.isEmpty()) {
            JSONObject content = candidates.getJSONObject(0).getJSONObject("content");
            JSONArray parts = content.getJSONArray("parts");
            if (!parts.isEmpty()) {
                return parts.getJSONObject(0).getString("text");
            }
        }
        return null;
    }
}
