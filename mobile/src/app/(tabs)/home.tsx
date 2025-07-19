import React, { useEffect, useState } from 'react';
import { View, Text, StyleSheet, ScrollView, ActivityIndicator } from 'react-native';
import { Image } from 'expo-image';
import { HomePageMainEvent } from '../../types/event_types';
import { getHomePageMainEvents } from '../../lib/api/event_api';

export default function HomeScreen() {
    const [mainEvents, setMainEvents] = useState<HomePageMainEvent[]>([]);
    const [loading, setLoading] = useState(true);
    const [error, setError] = useState<string | null>(null);

    useEffect(() => {
        fetchMainEvents();
    }, []);

    const fetchMainEvents = async () => {
        try {
            setLoading(true);
            setError(null);
            const fetchedMainEvents = await getHomePageMainEvents(3);
            setMainEvents(fetchedMainEvents);
        } catch (err) {
            setError(err instanceof Error ? err.message : 'An error occurred');
        } finally {
            setLoading(false);
        }
    };

    const formatFighterName = (fullName: string) => {
        const nameParts = fullName.trim().split(' ');
        if (nameParts.length === 1) {
            return { firstName: nameParts[0], lastName: '' };
        }
        const firstName = nameParts[0];
        const lastName = nameParts.slice(1).join(' ');
        return { firstName, lastName };
    };

    const renderEventCard = (event: HomePageMainEvent) => {
        const fighter1Name = formatFighterName(event.fighter_1_name);
        const fighter2Name = formatFighterName(event.fighter_2_name);

        return (
            <View key={event.event_id} style={styles.eventContainer}>
                <Text style={styles.eventTitle}>{event.event_title}</Text>
                <Text style={styles.eventDate}>
                    {new Date(event.event_date).toLocaleDateString()} at{' '}
                    {new Date(event.event_date).toLocaleTimeString([], { hour: '2-digit', minute: '2-digit' })}
                </Text>
                <View style={styles.fightCard}>
                    <View style={styles.fightersContainer}>
                        <View style={styles.fighter}>
                            <View style={styles.fighterImageContainer}>
                                {event.fighter_1_image ? (
                                    <Image
                                        source={{ uri: event.fighter_1_image }}
                                        style={styles.fighterImage}
                                        contentFit="cover"
                                        contentPosition="top"
                                    />
                                ) : null}
                            </View>
                            <View style={styles.fighterNameContainer}>
                                <Text style={styles.fighterFirstName}>{fighter1Name.firstName}</Text>
                                {fighter1Name.lastName !== '' && (
                                    <Text style={styles.fighterLastName}>{fighter1Name.lastName}</Text>
                                )}
                                {event.fighter_1_ranking && (
                                    <Text style={styles.fighterRank}>{'#' + event.fighter_1_ranking}</Text>
                                )}
                            </View>
                        </View>
                        <Text style={styles.vsText}>VS</Text>
                        <View style={styles.fighter}>
                            <View style={styles.fighterImageContainer}>
                                {event.fighter_2_image ? (
                                    <Image
                                        source={{ uri: event.fighter_2_image }}
                                        style={styles.fighterImage}
                                        contentFit="cover"
                                        contentPosition="top"
                                    />
                                ) : null}
                            </View>
                            <View style={styles.fighterNameContainer}>
                                <Text style={styles.fighterFirstName}>{fighter2Name.firstName}</Text>
                                {fighter2Name.lastName !== '' && (
                                    <Text style={styles.fighterLastName}>{fighter2Name.lastName}</Text>
                                )}
                                {event.fighter_2_ranking && (
                                    <Text style={styles.fighterRank}>{'#' + event.fighter_2_ranking}</Text>
                                )}
                            </View>
                        </View>
                    </View>
                </View>
            </View>
        );
    };

    return (
        <View style={styles.container}>
            {/* Header Banner - Fixed at top */}
            <View style={styles.header}>
                <View style={styles.headerContent}>
                    <Image source={require('../../../assets/images/brain.png')} style={styles.headerImage} />
                    <Text style={styles.headerText}>PredictMMA</Text>
                </View>
            </View>

            {/* Scrollable Content */}
            <ScrollView style={styles.scrollView}>
                <View style={styles.mainContent}>
                    <Text style={styles.welcomeTitle}>Upcoming Fights</Text>

                    {loading ? (
                        <ActivityIndicator size="large" color="#000" style={styles.loader} />
                    ) : error ? (
                        <Text style={styles.errorText}>Error: {error}</Text>
                    ) : mainEvents.length === 0 ? (
                        <Text style={styles.noEventsText}>No upcoming events found</Text>
                    ) : (
                        mainEvents.map(renderEventCard)
                    )}
                </View>
            </ScrollView>
        </View>
    );
}

const styles = StyleSheet.create({
    container: {
        flex: 1,
        backgroundColor: '#f5f5f5',
    },
    header: {
        backgroundColor: 'white',
        padding: 10,
        shadowColor: '#000',
        shadowOffset: {
            width: 0,
            height: 2,
        },
        shadowOpacity: 0.1,
        shadowRadius: 3.84,
        elevation: 5,
    },
    headerContent: {
        flexDirection: 'row',
        alignItems: 'center',
        justifyContent: 'center',
        marginTop: 50,
    },
    headerImage: {
        width: 36,
        height: 36,
        marginRight: 8,
    },
    headerText: {
        color: 'black',
        fontWeight: 'bold',
        fontSize: 18,
    },
    scrollView: {
        flex: 1,
    },
    mainContent: {
        paddingHorizontal: 16,
        paddingTop: 20,
        paddingBottom: 20,
    },
    welcomeTitle: {
        fontSize: 24,
        fontWeight: 'bold',
        marginBottom: 20,
        textAlign: 'center',
    },
    loader: {
        marginTop: 50,
    },
    errorText: {
        fontSize: 16,
        color: 'red',
        textAlign: 'center',
        marginTop: 20,
    },
    noEventsText: {
        fontSize: 16,
        color: '#666',
        textAlign: 'center',
        marginTop: 20,
    },
    eventContainer: {
        backgroundColor: 'white',
        borderRadius: 10,
        padding: 20,
        marginBottom: 20,
        shadowColor: '#000',
        shadowOffset: {
            width: 0,
            height: 2,
        },
        shadowOpacity: 0.1,
        shadowRadius: 3.84,
        elevation: 3,
    },
    eventTitle: {
        fontSize: 18,
        fontWeight: 'bold',
        marginBottom: 8,
        textAlign: 'center',
    },
    eventDate: {
        fontSize: 16,
        color: '#666',
        textAlign: 'center',
        marginBottom: 20,
    },
    fightCard: {
        padding: 16,
    },
    fightersContainer: {
        flexDirection: 'row',
        alignItems: 'center',
        justifyContent: 'space-between',
    },
    fighter: {
        flex: 1,
        alignItems: 'center',
    },
    fighterImageContainer: {
        width: 150,
        height: 150,
        borderRadius: 12,
        overflow: 'hidden',
        marginBottom: 12,
    },
    fighterImage: {
        width: 150,
        height: 150,
        resizeMode: 'cover',
    },
    fighterNameContainer: {
        alignItems: 'center',
        minHeight: 40,
        justifyContent: 'center',
    },
    fighterFirstName: {
        fontSize: 16,
        fontWeight: 'bold',
        textAlign: 'center',
        paddingHorizontal: 4,
    },
    fighterLastName: {
        fontSize: 16,
        fontWeight: 'bold',
        textAlign: 'center',
        paddingHorizontal: 4,
        marginTop: 2,
    },
    fighterRank: {
        fontSize: 12,
        color: '#888',
        marginTop: 2,
        fontWeight: '600',
        textAlign: 'center',
    },
    vsText: {
        fontSize: 24,
        fontWeight: 'bold',
        color: '#666',
        marginHorizontal: 20,
        marginTop: -26, // Shift upward to align with image center
    },
});
