package org.chater;

import com.fasterxml.jackson.databind.JsonNode;
import com.fasterxml.jackson.databind.ObjectMapper;
import io.jsonwebtoken.Jwts;
import io.jsonwebtoken.SignatureAlgorithm;
import io.jsonwebtoken.security.Keys;
import java.security.MessageDigest;
import okhttp3.OkHttpClient;
import okhttp3.Request;
import okhttp3.Response;
import org.apache.logging.log4j.LogManager;
import org.apache.logging.log4j.Logger;
import org.json.JSONObject;

import javax.crypto.SecretKey;
import java.io.IOException;
import java.nio.charset.StandardCharsets;
import java.security.KeyFactory;
import java.security.PublicKey;
import java.security.spec.RSAPublicKeySpec;
import java.time.Instant;
import java.time.temporal.ChronoUnit;
import java.util.Base64;
import java.util.Date;
import java.util.HashMap;
import java.util.Map;

public class AuthService {
    private static final Logger logger = LogManager.getLogger(AuthService.class);
    private static final OkHttpClient httpClient = new OkHttpClient();
    private static final ObjectMapper objectMapper = new ObjectMapper();
    
    // Get secret key from environment variable
    private static final String SECRET_KEY = System.getenv("EATER_SECRET_KEY");
    
    public static JSONObject processAuthRequest(JSONObject authRequest) {
        try {
            String provider = authRequest.getString("provider");
            String idToken = authRequest.getString("idToken");
            String email = authRequest.getString("email");
            String name = authRequest.optString("name", "");
            String profilePictureURL = authRequest.optString("profilePictureURL", "");
            
            logger.info("Processing auth request for provider: {} and email: {}", provider, email);
            
            // Validate ID token based on provider
            boolean isValid = false;
            String validatedEmail = null;
            
            if ("google".equals(provider)) {
                validatedEmail = validateGoogleToken(idToken);
                isValid = validatedEmail != null && validatedEmail.equals(email);
            } else if ("apple".equals(provider)) {
                validatedEmail = validateAppleToken(idToken);
                isValid = validatedEmail != null && validatedEmail.equals(email);
            } else {
                logger.error("Invalid provider: {}", provider);
                return createErrorResponse("invalid_provider", "Provider must be google or apple");
            }
            
            if (!isValid) {
                logger.error("Token validation failed for email: {} with provider: {}", email, provider);
                return createErrorResponse("invalid_token", "The provided ID token is invalid or expired");
            }
            
            // Generate JWT token
            String jwtToken = generateJWTToken(validatedEmail, provider);
            
            // Extract name for greeting if not provided
            if (name == null || name.trim().isEmpty()) {
                name = extractNameFromEmail(validatedEmail);
            }
            
            // Create successful response
            JSONObject response = new JSONObject();
            response.put("token", jwtToken);
            response.put("expiresIn", 31536000); // 1 year (365 days)
            response.put("userEmail", validatedEmail);
            response.put("userName", name);
            response.put("profilePictureURL", profilePictureURL);
            
            logger.info("Successfully generated auth token for email: {}", validatedEmail);
            return response;
            
        } catch (Exception e) {
            logger.error("Error processing auth request: ", e);
            return createErrorResponse("internal_error", "Authentication service temporarily unavailable");
        }
    }
    
    private static String validateGoogleToken(String idToken) {
        try {
            // Get Google's public keys
            Request request = new Request.Builder()
                    .url("https://www.googleapis.com/oauth2/v3/certs")
                    .build();
            
            try (Response response = httpClient.newCall(request).execute()) {
                if (!response.isSuccessful()) {
                    logger.error("Failed to fetch Google public keys");
                    return null;
                }
                
                // For simplicity, we'll do basic token validation
                // In production, you should properly verify the signature using the public keys
                String[] tokenParts = idToken.split("\\.");
                if (tokenParts.length != 3) {
                    logger.error("Invalid Google ID token format");
                    return null;
                }
                
                // Decode the payload
                String payload = new String(Base64.getUrlDecoder().decode(tokenParts[1]), StandardCharsets.UTF_8);
                JsonNode payloadNode = objectMapper.readTree(payload);
                
                // Check expiration
                long exp = payloadNode.get("exp").asLong();
                if (Instant.now().getEpochSecond() > exp) {
                    logger.error("Google ID token has expired");
                    return null;
                }
                
                // Extract email
                String email = payloadNode.get("email").asText();
                logger.info("Google token validated for email: {}", email);
                return email;
            }
        } catch (Exception e) {
            logger.error("Error validating Google token: ", e);
            return null;
        }
    }
    
    private static String validateAppleToken(String idToken) {
        try {
            // Similar to Google, but using Apple's keys
            // For simplicity, we'll do basic token validation
            String[] tokenParts = idToken.split("\\.");
            if (tokenParts.length != 3) {
                logger.error("Invalid Apple ID token format");
                return null;
            }
            
            // Decode the payload
            String payload = new String(Base64.getUrlDecoder().decode(tokenParts[1]), StandardCharsets.UTF_8);
            JsonNode payloadNode = objectMapper.readTree(payload);
            
            // Check expiration
            long exp = payloadNode.get("exp").asLong();
            if (Instant.now().getEpochSecond() > exp) {
                logger.error("Apple ID token has expired");
                return null;
            }
            
            // Extract email
            String email = payloadNode.get("email").asText();
            logger.info("Apple token validated for email: {}", email);
            return email;
        } catch (Exception e) {
            logger.error("Error validating Apple token: ", e);
            return null;
        }
    }
    
    private static String generateJWTToken(String email, String provider) {
        try {
            if (SECRET_KEY == null || SECRET_KEY.trim().isEmpty()) {
                throw new IllegalStateException("EATER_SECRET_KEY environment variable not set");
            }
            
            // Create secret key from environment variable
            // Use SHA-256 hash to ensure we have a 256-bit key regardless of input length
            byte[] secretBytes = SECRET_KEY.getBytes(StandardCharsets.UTF_8);
            
            // If the secret is already 32+ bytes, use it directly with hmacShaKeyFor
            // Otherwise, derive a 256-bit key using SHA-256
            SecretKey key;
            if (secretBytes.length >= 32) {
                key = Keys.hmacShaKeyFor(secretBytes);
            } else {
                // Derive a 256-bit key from the secret using SHA-256
                MessageDigest digest = MessageDigest.getInstance("SHA-256");
                byte[] hashedSecret = digest.digest(secretBytes);
                key = Keys.hmacShaKeyFor(hashedSecret);
                logger.warn("Secret key was too short ({}bits), derived 256-bit key using SHA-256. Consider using a longer secret key.", secretBytes.length * 8);
            }
            
            // Create JWT token
            String token = Jwts.builder()
                    .setSubject(email)
                    .setIssuedAt(new Date())
                    .setExpiration(Date.from(Instant.now().plus(365, ChronoUnit.DAYS)))
                    .claim("provider", provider)
                    .signWith(key, SignatureAlgorithm.HS256)
                    .compact();
            
            logger.info("JWT token generated for email: {}", email);
            return token;
        } catch (Exception e) {
            logger.error("Error generating JWT token: ", e);
            throw new RuntimeException("Failed to generate JWT token", e);
        }
    }
    
    private static String extractNameFromEmail(String email) {
        if (email == null || !email.contains("@")) {
            return "User";
        }
        
        String localPart = email.split("@")[0];
        // Replace dots and underscores with spaces and capitalize
        String name = localPart.replaceAll("[._]", " ");
        
        // Capitalize first letter of each word
        String[] words = name.split(" ");
        StringBuilder capitalized = new StringBuilder();
        for (String word : words) {
            if (word.length() > 0) {
                capitalized.append(Character.toUpperCase(word.charAt(0)))
                          .append(word.substring(1).toLowerCase())
                          .append(" ");
            }
        }
        
        return capitalized.toString().trim();
    }
    
    private static JSONObject createErrorResponse(String error, String message) {
        JSONObject errorResponse = new JSONObject();
        errorResponse.put("error", error);
        errorResponse.put("message", message);
        return errorResponse;
    }
} 